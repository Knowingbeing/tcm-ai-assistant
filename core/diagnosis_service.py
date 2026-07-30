"""问诊分析编排：安全层 -> RAG -> 结构化模型输出。"""

from __future__ import annotations

from typing import Any, Dict, List

from core.knowledge_retriever import get_default_retriever
from core.safety import assess_safety, safety_block_result
from core.schemas import PROMPT_VERSION, make_symptom_profile, validate_diagnosis_result


def analyze_consultation(
    engine: Any,
    chief_complaint: str,
    symptoms: List[str],
    tongue_sign: str = "",
    pulse_sign: str = "",
    ten_asks_data: Dict[str, Any] | None = None,
    patient: Dict[str, Any] | None = None,
    followups: List[Dict[str, Any]] | None = None,
    top_k: int = 8,
) -> Dict[str, Any]:
    profile = make_symptom_profile(
        chief_complaint,
        symptoms,
        tongue_sign,
        pulse_sign,
        ten_asks_data=ten_asks_data,
        patient=patient,
        followups=followups,
    )
    safety = assess_safety(profile)
    retriever = get_default_retriever()
    hits = retriever.retrieve(chief_complaint, symptoms, tongue_sign, pulse_sign, top_k=top_k)

    if safety.blocked:
        result, warnings = validate_diagnosis_result(
            safety_block_result(profile, safety),
            profile,
            hits,
            model_status="blocked_by_safety",
        )
        result["validation_warnings"] = warnings
    else:
        result = engine.analyze_with_rag(
            chief_complaint,
            symptoms,
            tongue_sign,
            pulse_sign,
            knowledge_hits=hits,
            safety_context=safety.to_dict(),
        )

    safety_warnings = list(dict.fromkeys((result.get("risk_warnings") or []) + safety.warnings))
    result.update({
        "symptom_profile": profile,
        "missing_fields": profile.get("missing_fields", []),
        "retrieval_ids": [hit.item.id for hit in hits],
        "retrieval_hits": [hit.to_dict() for hit in hits],
        "safety_tags": safety.tags,
        "safety_assessment": safety.to_dict(),
        "risk_warnings": safety_warnings,
        "prompt_version": PROMPT_VERSION,
        "handoff_required": bool(result.get("needs_human_handoff") or safety.handoff_required),
        "handoff_reason": result.get("handoff_reason") or safety.handoff_reason,
        "immediate_care_recommended": bool(result.get("immediate_care_recommended") or safety.immediate_care),
    })
    return result

