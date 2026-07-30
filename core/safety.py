"""医疗安全规则层。

安全提示由规则层固定输出，模型不得弱化或改写。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List

from core.schemas import clean_text, information_completeness, missing_core_fields, safe_list


EMERGENCY_SIGNALS = {
    "胸痛": ["胸痛", "胸口压榨", "胸闷憋气", "心前区痛"],
    "呼吸困难": ["呼吸困难", "喘不过气", "气促", "窒息感", "口唇发紫"],
    "意识障碍": ["意识不清", "昏迷", "晕厥", "抽搐", "言语不清", "偏瘫"],
    "大量出血": ["大量出血", "便血不止", "呕血", "咯血", "阴道大出血"],
    "高热不退": ["高热不退", "持续高热", "体温40", "体温 40", "高烧三天", "高烧不退"],
    "严重过敏": ["喉头水肿", "全身风团", "严重过敏", "过敏性休克"],
    "自伤风险": ["自杀", "轻生", "不想活", "自残", "伤害自己"],
}

PREGNANCY_RISK = ["孕", "怀孕", "妊娠", "胎动异常", "阴道出血", "腹痛"]
PRESCRIPTION_REQUEST = ["开方", "处方", "直接给药", "照方服药", "剂量怎么吃", "替代医生", "确诊"]


@dataclass
class SafetyAssessment:
    blocked: bool = False
    tags: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    handoff_required: bool = False
    handoff_reason: str = ""
    immediate_care: bool = False
    missing_fields: List[str] = field(default_factory=list)
    information_completeness: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _join_profile_text(profile: Dict[str, Any]) -> str:
    ten_asks = profile.get("ten_asks_data") or {}
    fragments = [
        profile.get("chief_complaint", ""),
        " ".join(safe_list(profile.get("symptoms"))),
        profile.get("tongue_sign", ""),
        profile.get("pulse_sign", ""),
    ]
    for value in ten_asks.values():
        if isinstance(value, dict):
            fragments.extend(str(v) for v in value.values())
        else:
            fragments.append(str(value))
    return " ".join(clean_text(v, 300) for v in fragments if v)


def assess_safety(profile: Dict[str, Any]) -> SafetyAssessment:
    text = _join_profile_text(profile)
    patient = profile.get("patient") or {}
    missing = missing_core_fields(profile)
    completeness = information_completeness(profile)
    assessment = SafetyAssessment(
        missing_fields=missing,
        information_completeness=completeness,
    )

    for tag, keywords in EMERGENCY_SIGNALS.items():
        if any(keyword in text for keyword in keywords):
            assessment.tags.append(tag)
            assessment.blocked = True
            assessment.immediate_care = True

    gender = str(patient.get("gender", ""))
    if ("女" in gender or any(keyword in text for keyword in PREGNANCY_RISK[:3])) and any(keyword in text for keyword in PREGNANCY_RISK):
        if any(keyword in text for keyword in ["阴道出血", "腹痛", "胎动异常", "高热"]):
            assessment.tags.append("孕期高风险")
            assessment.blocked = True
            assessment.immediate_care = True

    try:
        age = int(patient.get("age", 0) or 0)
    except Exception:
        age = 0
    if age and (age < 6 or age >= 75):
        assessment.tags.append("特殊年龄人群")
        assessment.warnings.append("儿童或高龄人群症状变化可能较快，建议由专业医师确认。")
        assessment.handoff_required = True

    if any(keyword in text for keyword in PRESCRIPTION_REQUEST):
        assessment.tags.append("处方替代请求")
        assessment.blocked = True
        assessment.handoff_required = True
        assessment.handoff_reason = "用户请求直接开方或替代医生诊断，产品仅能提供知识辅助。"

    if completeness < 45:
        assessment.tags.append("信息严重不足")
        assessment.handoff_required = True
        if not assessment.handoff_reason:
            assessment.handoff_reason = "问诊信息严重不足，不能形成可靠辨证。"

    if assessment.immediate_care:
        assessment.handoff_required = True
        assessment.handoff_reason = "命中急症或高风险信号，应优先线下及时就医。"
        assessment.warnings.insert(0, "当前信息包含急症或高风险信号，请及时联系急救或前往正规医疗机构。")

    if not assessment.warnings:
        assessment.warnings.append("本产品仅用于中医知识辅助和问诊信息结构化，不替代执业医师诊断或治疗。")
    return assessment


def safety_block_result(profile: Dict[str, Any], assessment: SafetyAssessment) -> Dict[str, Any]:
    return {
        "information_completeness": assessment.information_completeness,
        "suggested_followups": [],
        "possible_syndromes": [],
        "syndrome": "已触发安全拦截",
        "syndrome_category": "医疗安全",
        "analysis_basis": assessment.warnings,
        "formula": "不提供方剂建议",
        "formula_adjustment": "",
        "treatment_principle": "请优先寻求线下医疗帮助",
        "treatment_knowledge": "",
        "analysis": "因命中安全规则，本次不会进入普通辨证流程，也不会生成处方或确定性诊断。",
        "risk_warnings": assessment.warnings,
        "confidence": 0,
        "needs_human_handoff": True,
        "handoff_reason": assessment.handoff_reason,
        "immediate_care_recommended": assessment.immediate_care,
        "model_status": "blocked_by_safety",
        "safety_tags": assessment.tags,
    }

