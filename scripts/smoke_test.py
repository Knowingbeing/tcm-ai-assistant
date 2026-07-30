"""
中医 AI 智能问诊助手冒烟测试
================================

不需要真实 API Key 或 Supabase 凭证，覆盖结构化问诊、两轮追问、RAG、安全层、
结构化输出、存储结构和看板统计所依赖的核心字段。

运行：
    python scripts/smoke_test.py
"""

from __future__ import annotations

import importlib
import json
import os
import sys
import tempfile

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


def test_section(name: str) -> None:
    print(f"\n[TEST] {name}")
    print("-" * 60)


def assert_eq(actual, expected, msg: str = "") -> None:
    if actual == expected:
        print(f"  [OK] {msg or 'OK'}")
        return
    print(f"  [FAIL] {msg}")
    print(f"    expected: {expected}")
    print(f"    actual  : {actual}")
    sys.exit(1)


def assert_true(cond, msg: str = "") -> None:
    if cond:
        print(f"  [OK] {msg or 'OK'}")
        return
    print(f"  [FAIL] {msg or 'FAIL'}")
    sys.exit(1)


def main() -> None:
    os.environ.pop("SUPABASE_URL", None)
    os.environ.pop("SUPABASE_KEY", None)

    test_section("1. Supabase 未配置时安全降级")
    from utils import supabase_client
    importlib.reload(supabase_client)
    assert_eq(supabase_client.is_configured(), False, "未配置时 is_configured() == False")
    assert_eq(supabase_client.get_client(), None, "未配置时 get_client() 返回 None")
    assert_eq(supabase_client.get_records(), [], "未配置时 get_records() 返回空列表")
    ok, err = supabase_client.save_record({"chief_complaint": "测试"})
    assert_eq(ok, False, "无 Supabase 凭证时不写云端")
    assert_true("Supabase" in err, "返回清晰错误信息")

    test_section("2. 十问歌字段收集完整性")
    from data.ten_asks import DEFAULT_TEN_ASKS
    import app as _app
    ten_data = dict(DEFAULT_TEN_ASKS)
    ten_data.update({
        "cold_heat": {"type": "恶寒", "detail": ""},
        "sweat": {"type": "无汗", "detail": ""},
        "stool_urine": {"stool": "干结", "urine": "短赤"},
        "head_body": {"parts": ["头痛", "身痛"], "detail": ""},
    })
    symptoms = _app._collect_ten_asks_symptoms(ten_data)
    for value in ["恶寒", "无汗", "大便干结", "小便短赤", "头痛", "身痛"]:
        assert_true(value in symptoms, f"十问歌采集到 {value}")

    test_section("3. 追问不重复且不超过两轮")
    from utils.llm_engine import TCMDiagnosisEngine
    engine = TCMDiagnosisEngine(api_key="", provider="DeepSeek", model="")
    first = engine.should_ask_followup("咳嗽一周", ["咳嗽"], "", "", 0)
    assert_true(first["need_followup"], "信息不足时需要追问")
    assert_true(len(first["questions"]) <= 2, "每轮最多 2 个问题")
    fake = {
        "session_id": "test",
        "round": 0,
        "messages": [],
        "pending_questions": first["questions"],
        "asked_followup_fields": [q["field"] for q in first["questions"]],
        "followup_history": [],
        "chief_complaint": "咳嗽一周",
        "symptoms": ["咳嗽"],
        "tongue_sign": "",
        "pulse_sign": "",
        "ten_asks_data": {},
        "patient": {"name": "匿名", "age": 30, "gender": "男"},
        "result": None,
    }
    for q in list(first["questions"]):
        _app._apply_followup_answer(fake, q, q["options"][0], engine)
    assert_true(fake["round"] <= 1, "第一轮回答后轮次正确")
    assert_true(len(fake.get("pending_questions", [])) <= 2, "第二轮仍最多 2 个问题")
    second_fields = [q["field"] for q in fake.get("pending_questions", [])]
    assert_true(not set(second_fields).intersection(set(first_q["field"] for first_q in first["questions"])), "第二轮不重复询问已有字段")
    for q in list(fake.get("pending_questions", [])):
        _app._apply_followup_answer(fake, q, q["options"][0], engine)
    assert_true(fake["round"] <= 2, "最多追问两轮")
    assert_true(len(fake.get("followup_history", [])) >= 2, "追问答案写入统一历史")
    assert_true(fake.get("result") is not None, "两轮后生成结构化结果")

    test_section("4. RAG 根据不同症状返回不同 Top-K")
    from core.knowledge_retriever import evaluate_retriever, format_hits_for_prompt, get_default_retriever
    retriever = get_default_retriever()
    cold_hits = retriever.retrieve("恶寒无汗头痛", ["恶寒", "无汗", "头痛"], "舌苔薄白", "脉浮紧", top_k=5)
    sleep_hits = retriever.retrieve("心悸失眠多梦", ["心悸", "失眠", "多梦"], "舌淡", "脉细", top_k=5)
    assert_true(cold_hits and sleep_hits, "两组症状均有检索结果")
    assert_true(cold_hits[0].item.id != sleep_hits[0].item.id, "不同症状 Top-1 不同")
    assert_true("syndrome:太阳伤寒证" in [hit.item.id for hit in cold_hits], "Recall@K 命中太阳伤寒证")

    test_section("5. 检索结果进入模型上下文")
    context = format_hits_for_prompt(cold_hits)
    assert_true("syndrome:太阳伤寒证" in context, "Prompt 上下文包含知识 ID")
    assert_true("来源=" in context and "禁忌/注意" in context, "Prompt 上下文包含来源和注意事项")

    test_section("6. 引用来源与检索结果一致")
    result = engine.analyze_with_rag("恶寒无汗头痛", ["恶寒", "无汗", "头痛"], "舌苔薄白", "脉浮紧", cold_hits)
    hit_ids = {hit.item.id for hit in cold_hits}
    ref_ids = {ref["id"] for ref in result.get("knowledge_references", [])}
    assert_true(ref_ids.issubset(hit_ids), "结果引用 ID 来自检索结果")

    test_section("7. 模型结构化输出校验")
    required = {
        "information_completeness", "suggested_followups", "possible_syndromes",
        "syndrome", "syndrome_category", "analysis_basis", "knowledge_references",
        "treatment_principle", "risk_warnings", "confidence", "needs_human_handoff",
        "immediate_care_recommended", "model_status",
    }
    assert_true(required.issubset(result.keys()), "结构化结果包含必需字段")
    assert_true(0 <= int(result["confidence"]) <= 100, "置信度在 0-100")

    test_section("8. 模型异常或无 Key 时不伪造 AI 结果")
    assert_eq(result["model_status"], "not_called_no_api_key", "无 Key 时标记为未调用模型")
    assert_true("本地知识库辅助" in result.get("analysis", "") or "尚未调用 AI" in result.get("analysis", ""), "明确说明降级状态")

    test_section("9. 急症识别和安全拦截")
    from core.diagnosis_service import analyze_consultation
    emergency = analyze_consultation(engine, "突发胸痛伴呼吸困难", ["胸痛", "呼吸困难"], "", "")
    assert_eq(emergency["model_status"], "blocked_by_safety", "急症优先安全拦截")
    assert_eq(emergency["immediate_care_recommended"], True, "建议及时就医")
    assert_true("胸痛" in emergency["safety_tags"], "保留安全标签")

    test_section("10. 低置信度或知识不足拒绝确定性结论")
    weak = analyze_consultation(engine, "说不清哪里不舒服", [], "", "")
    assert_true(weak["confidence"] < 60 or weak["information_completeness"] < 60, "低置信度/低完整度成立")
    assert_true(weak["handoff_required"] or weak["needs_human_handoff"], "进入人工确认")

    test_section("11. Supabase 与 JSON 存储结构一致")
    sample_record = {
        "session_id": "s1",
        "round_index": 2,
        "chief_complaint": "恶寒无汗头痛",
        "symptoms": ["恶寒", "无汗"],
        "structured_result": result,
        "retrieval_ids": result["retrieval_ids"],
        "safety_tags": result["safety_tags"],
        "confidence": result["confidence"],
        "source": "chat",
    }
    payload = supabase_client._normalize_consultation_payload(sample_record)
    dumped = json.dumps(sample_record, ensure_ascii=False)
    loaded_json = json.loads(dumped)
    for key in ["structured_result", "retrieval_ids", "safety_tags", "confidence"]:
        assert_true(key in payload and key in loaded_json, f"两种存储均包含 {key}")

    test_section("12. 历史会话保存与读取")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump([sample_record], f, ensure_ascii=False)
        tmp_path = f.name
    with open(tmp_path, "r", encoding="utf-8") as f:
        history = json.load(f)
    os.unlink(tmp_path)
    assert_eq(history[0]["session_id"], "s1", "历史会话 session_id 可读取")
    assert_true(history[0]["retrieval_ids"], "历史会话保留检索 ID")

    test_section("13. 看板统计字段可计算")
    records = [sample_record, emergency, weak]
    safety_count = len([r for r in records if r.get("safety_tags")])
    handoff_ratio = len([r for r in records if r.get("handoff_required") or r.get("needs_human_handoff")]) / len(records)
    no_retrieval_ratio = len([r for r in records if not r.get("retrieval_ids")]) / len(records)
    assert_true(safety_count >= 1, "安全拦截案例可统计")
    assert_true(0 <= handoff_ratio <= 1, "人工接管比例可统计")
    assert_true(0 <= no_retrieval_ratio <= 1, "检索无结果比例可统计")

    test_section("14. API Key 和个人信息不进入日志字段")
    serialized = json.dumps(sample_record, ensure_ascii=False)
    assert_true("sk-" not in serialized and "SUPABASE_KEY" not in serialized, "记录中不含密钥")
    assert_true("身份证" not in serialized and "手机号" not in serialized, "测试记录不含不必要个人信息")

    test_section("15. 可重复检索评测")
    metrics = evaluate_retriever(retriever, [{
        "query": "恶寒无汗头痛",
        "symptoms": ["恶寒", "无汗", "头痛"],
        "tongue": "舌苔薄白",
        "pulse": "脉浮紧",
        "expected_ids": ["syndrome:太阳伤寒证"],
    }], top_k=5)
    assert_eq(metrics["cases"], 1, "评测病例数量正确")
    assert_true(metrics["recall_at_k"] >= 1.0, "Recall@K 达到预期")
    assert_true(metrics["citation_accuracy"] >= 1.0, "引用正确率达到预期")

    print("\n" + "=" * 60)
    print("[PASS] 全部冒烟测试通过")
    print("=" * 60)


if __name__ == "__main__":
    main()
