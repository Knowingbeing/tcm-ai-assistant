"""结构化问诊与模型输出校验。

本模块不依赖外部包，用 dataclass + 显式校验实现 Pydantic 等效的边界约束。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, Iterable, List, Tuple


PROMPT_VERSION = "rag-safety-v1.0"
KNOWLEDGE_VERSION = "2026.07"

CORE_INFO_FIELDS = {
    "cold_heat": "寒热",
    "sweat": "汗",
    "stool_urine": "二便",
    "tongue_sign": "舌象",
    "pulse_sign": "脉象",
}


def clean_text(value: Any, max_len: int = 500) -> str:
    """清洗用户输入，避免过长文本和明显控制字符进入模型或日志。"""
    if value is None:
        return ""
    text = str(value).replace("\x00", "").strip()
    text = "".join(ch for ch in text if ch == "\n" or ch == "\t" or ord(ch) >= 32)
    return text[:max_len]


def safe_list(value: Any, max_items: int = 80, max_len: int = 120) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, Iterable):
        return []
    result: List[str] = []
    for item in value:
        text = clean_text(item, max_len=max_len)
        if text and text not in result:
            result.append(text)
        if len(result) >= max_items:
            break
    return result


def clamp_confidence(value: Any) -> int:
    try:
        return max(0, min(100, int(round(float(value)))))
    except Exception:
        return 0


def make_symptom_profile(
    chief_complaint: str,
    symptoms: Iterable[str] | None,
    tongue_sign: str = "",
    pulse_sign: str = "",
    ten_asks_data: Dict[str, Any] | None = None,
    patient: Dict[str, Any] | None = None,
    followups: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    profile = {
        "chief_complaint": clean_text(chief_complaint, 800),
        "symptoms": safe_list(symptoms),
        "tongue_sign": clean_text(tongue_sign, 120),
        "pulse_sign": clean_text(pulse_sign, 120),
        "ten_asks_data": ten_asks_data or {},
        "patient": patient or {},
        "followups": followups or [],
    }
    profile["missing_fields"] = missing_core_fields(profile)
    profile["information_completeness"] = information_completeness(profile)
    return profile


def _has_field_info(profile: Dict[str, Any], field: str) -> bool:
    if field == "tongue_sign":
        return bool(clean_text(profile.get("tongue_sign")))
    if field == "pulse_sign":
        return bool(clean_text(profile.get("pulse_sign")))
    ten_asks = profile.get("ten_asks_data") or {}
    if field == "stool_urine":
        block = ten_asks.get("stool_urine", {})
        return bool(clean_text(block.get("stool")) or clean_text(block.get("urine")))
    block = ten_asks.get(field, {})
    if isinstance(block, dict):
        return any(bool(clean_text(v)) for v in block.values())
    return bool(clean_text(block))


def missing_core_fields(profile: Dict[str, Any]) -> List[str]:
    missing = []
    for field, label in CORE_INFO_FIELDS.items():
        if not _has_field_info(profile, field):
            missing.append(label)
    if not clean_text(profile.get("chief_complaint")):
        missing.insert(0, "主诉")
    return missing


def information_completeness(profile: Dict[str, Any]) -> int:
    checks = [
        bool(clean_text(profile.get("chief_complaint"))),
        bool(safe_list(profile.get("symptoms"))),
        _has_field_info(profile, "cold_heat"),
        _has_field_info(profile, "sweat"),
        _has_field_info(profile, "stool_urine"),
        _has_field_info(profile, "tongue_sign"),
        _has_field_info(profile, "pulse_sign"),
    ]
    return int(round(sum(1 for ok in checks if ok) / len(checks) * 100))


@dataclass
class KnowledgeReference:
    id: str
    type: str
    name: str
    source: str = "本地知识库"
    score: float = 0.0


@dataclass
class SyndromeCandidate:
    name: str
    category: str = "待分类"
    confidence: int = 0
    basis: str = ""
    knowledge_ids: List[str] = field(default_factory=list)


@dataclass
class StructuredDiagnosis:
    information_completeness: int = 0
    suggested_followups: List[Dict[str, Any]] = field(default_factory=list)
    possible_syndromes: List[SyndromeCandidate] = field(default_factory=list)
    syndrome: str = "暂不形成确定性结论"
    syndrome_category: str = "待确认"
    analysis_basis: List[str] = field(default_factory=list)
    knowledge_references: List[KnowledgeReference] = field(default_factory=list)
    formula: str = "知识参考，非处方"
    formula_adjustment: str = ""
    treatment_principle: str = "需四诊合参后由专业人士判断"
    treatment_knowledge: str = ""
    analysis: str = ""
    risk_warnings: List[str] = field(default_factory=list)
    confidence: int = 0
    needs_human_handoff: bool = True
    handoff_reason: str = "需要人工确认"
    immediate_care_recommended: bool = False
    model_status: str = "not_called"
    prompt_version: str = PROMPT_VERSION
    structured_output_valid: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def references_from_hits(hits: Iterable[Any]) -> List[KnowledgeReference]:
    refs: List[KnowledgeReference] = []
    for hit in hits or []:
        item = getattr(hit, "item", hit)
        refs.append(
            KnowledgeReference(
                id=str(getattr(item, "id", item.get("id", "")) if isinstance(item, dict) else getattr(item, "id", "")),
                type=str(getattr(item, "type", item.get("type", "")) if isinstance(item, dict) else getattr(item, "type", "")),
                name=str(getattr(item, "name", item.get("name", "")) if isinstance(item, dict) else getattr(item, "name", "")),
                source=str(getattr(item, "source", item.get("source", "本地知识库")) if isinstance(item, dict) else getattr(item, "source", "本地知识库")),
                score=float(getattr(hit, "score", 0.0) or 0.0),
            )
        )
    return refs


def validate_diagnosis_result(
    raw: Dict[str, Any] | None,
    profile: Dict[str, Any] | None = None,
    knowledge_hits: Iterable[Any] | None = None,
    model_status: str = "ok",
) -> Tuple[Dict[str, Any], List[str]]:
    """把模型或本地辅助结果规整为固定 Schema。"""
    raw = raw or {}
    profile = profile or {}
    warnings: List[str] = []
    references = references_from_hits(knowledge_hits or raw.get("knowledge_references") or [])
    completeness = clamp_confidence(raw.get("information_completeness", profile.get("information_completeness", 0)))
    confidence = clamp_confidence(raw.get("confidence", 0))

    possible = []
    raw_candidates = raw.get("possible_syndromes")
    if isinstance(raw_candidates, list):
        for cand in raw_candidates[:5]:
            if not isinstance(cand, dict):
                continue
            possible.append(
                SyndromeCandidate(
                    name=clean_text(cand.get("name") or cand.get("syndrome") or "待辨证", 80),
                    category=clean_text(cand.get("category") or cand.get("syndrome_category") or "待分类", 80),
                    confidence=clamp_confidence(cand.get("confidence", confidence)),
                    basis=clean_text(cand.get("basis", ""), 500),
                    knowledge_ids=safe_list(cand.get("knowledge_ids"), max_items=12, max_len=80),
                )
            )
    if not possible and clean_text(raw.get("syndrome")):
        possible.append(
            SyndromeCandidate(
                name=clean_text(raw.get("syndrome"), 80),
                category=clean_text(raw.get("syndrome_category", "待分类"), 80),
                confidence=confidence,
                basis=clean_text(raw.get("analysis", ""), 500),
                knowledge_ids=[ref.id for ref in references[:3]],
            )
        )

    result = StructuredDiagnosis(
        information_completeness=completeness,
        suggested_followups=raw.get("suggested_followups") if isinstance(raw.get("suggested_followups"), list) else [],
        possible_syndromes=possible,
        syndrome=clean_text(raw.get("syndrome") or (possible[0].name if possible else "暂不形成确定性结论"), 80),
        syndrome_category=clean_text(raw.get("syndrome_category") or (possible[0].category if possible else "待确认"), 80),
        analysis_basis=safe_list(raw.get("analysis_basis") or [raw.get("analysis", "")], max_items=10, max_len=500),
        knowledge_references=references,
        formula=clean_text(raw.get("formula") or "知识参考，非处方", 120),
        formula_adjustment=clean_text(raw.get("formula_adjustment", ""), 500),
        treatment_principle=clean_text(raw.get("treatment_principle") or "需四诊合参后由专业人士判断", 180),
        treatment_knowledge=clean_text(raw.get("treatment_knowledge") or raw.get("treatment_principle", ""), 800),
        analysis=clean_text(raw.get("analysis", ""), 1200),
        risk_warnings=safe_list(raw.get("risk_warnings"), max_items=12, max_len=300),
        confidence=confidence,
        needs_human_handoff=bool(raw.get("needs_human_handoff", confidence < 60 or completeness < 70)),
        handoff_reason=clean_text(raw.get("handoff_reason") or ("置信度或信息完整度不足" if confidence < 60 or completeness < 70 else ""), 300),
        immediate_care_recommended=bool(raw.get("immediate_care_recommended", False)),
        model_status=clean_text(raw.get("model_status") or model_status, 80),
        structured_output_valid=True,
    )

    required = ["information_completeness", "possible_syndromes", "analysis_basis", "risk_warnings", "confidence"]
    for key in required:
        if key not in raw:
            warnings.append(f"模型输出缺少字段：{key}")
    if not result.analysis and result.analysis_basis:
        result.analysis = "；".join(result.analysis_basis[:3])
    if confidence < 60:
        result.syndrome = "暂不形成确定性结论"
    return result.to_dict(), warnings

