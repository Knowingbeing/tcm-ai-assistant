import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
from datetime import datetime
import sys

sys.path.append(os.path.dirname(__file__))
from utils.llm_engine import TCMDiagnosisEngine, API_PROVIDERS, DEFAULT_API_KEY, DEFAULT_PROVIDER
from data.tcm_data import FORMULAS, SYNDROMES, HERBS

st.set_page_config(
    page_title="中医AI智能问诊助手",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 50%, #388E3C 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        color: white !important;
        margin: 0;
        font-size: 2rem;
    }
    .main-header p {
        color: rgba(255,255,255,0.9);
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #2E7D32;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }
    .section-header {
        background: #E8F5E9;
        padding: 0.8rem 1.2rem;
        border-radius: 8px;
        border-left: 4px solid #2E7D32;
        margin: 1rem 0;
    }
    .section-header h2, .section-header h3 {
        color: #1B5E20 !important;
        margin: 0;
        font-size: 1.1rem;
    }
    .info-box {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #A5D6A7;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    div[data-testid="stMetric"] {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #E8F5E9;
    }
    div[data-testid="stMetric"] label {
        color: #2E7D32 !important;
        font-weight: 600 !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: #2E7D32 !important;
        color: white !important;
    }
    div[data-baseweb="tab-panel"] {
        padding: 1rem 0;
    }
    .diagnosis-result {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #A5D6A7;
        margin: 1rem 0;
    }
    .herb-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #E8F5E9;
        margin-bottom: 0.5rem;
    }
    .warning-box {
        background: #FFF3E0;
        border: 1px solid #FFE0B2;
        border-radius: 8px;
        padding: 0.8rem;
        color: #E65100;
    }
</style>
""", unsafe_allow_html=True)

DATA_DIR = "/tmp" if os.path.exists("/tmp") else "data"
os.makedirs(DATA_DIR, exist_ok=True)
RECORDS_FILE = os.path.join(DATA_DIR, "tcm_records.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "tcm_settings.json")

def load_records():
    if os.path.exists(RECORDS_FILE):
        try:
            with open(RECORDS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_records(records):
    with open(RECORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"api_key": DEFAULT_API_KEY, "provider": DEFAULT_PROVIDER, "model": ""}

def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

def get_engine():
    settings = load_settings()
    api_key = settings.get("api_key", DEFAULT_API_KEY)
    provider = settings.get("provider", DEFAULT_PROVIDER)
    model = settings.get("model", "")

    engine_key = f"{provider}:{api_key}"
    if "engine" not in st.session_state or st.session_state.get("engine_key") != engine_key:
        st.session_state.engine = TCMDiagnosisEngine(api_key, provider, model)
        st.session_state.engine_key = engine_key
    return st.session_state.engine

def main():
    engine = get_engine()

    st.markdown("""
    <div class="main-header">
        <h1>🏥 中医AI智能问诊助手</h1>
        <p>基于 LLM + RAG 架构的中医智能问诊系统 | 支持六经/脏腑/气血津液辨证</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 智能问诊", "📊 数据分析", "📚 知识库", "🌿 中药库", "⚙️ 系统设置"])

    with tab1:
        render_consultation_tab(engine)
    with tab2:
        render_analytics_tab()
    with tab3:
        render_knowledge_tab()
    with tab4:
        render_herb_tab()
    with tab5:
        render_settings_tab()

def render_consultation_tab(engine):
    st.markdown('<div class="section-header"><h2>📋 智能问诊</h2></div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 3])

    with col1:
        st.subheader("患者信息")
        patient_name = st.text_input("姓名", placeholder="请输入患者姓名")
        patient_age = st.number_input("年龄", min_value=0, max_value=150, value=30)
        patient_gender = st.selectbox("性别", ["男", "女"])

        st.subheader("问诊信息")
        chief_complaint = st.text_area("主诉", placeholder="请描述主要症状，如：头痛、发热3天", height=100)

        st.subheader("症状选择")
        all_symptoms = ["发热", "恶寒", "畏寒", "头痛", "头晕", "咳嗽", "鼻塞", "流涕",
                       "咽喉痛", "胸闷", "心悸", "腹痛", "腹泻", "便秘", "食欲不振",
                       "口渴", "口苦", "失眠", "乏力", "自汗", "盗汗", "腰膝酸软",
                       "畏寒肢冷", "呕吐", "腹胀", "胸胁胀痛", "善太息", "情志抑郁",
                       "面红目赤", "急躁易怒", "眩晕", "耳鸣", "多梦", "健忘",
                       "气短", "神疲", "四肢厥冷", "干咳少痰", "痰多", "痰黄稠",
                       "关节疼痛", "身热不扬", "心烦", "消渴", "刺痛", "面色晦暗"]
        selected_symptoms = st.multiselect("请选择伴随症状", all_symptoms)

        st.subheader("舌脉信息")
        tongue_sign = st.text_input("舌象", placeholder="如：舌苔薄白、舌质淡红")
        pulse_sign = st.text_input("脉象", placeholder="如：脉浮紧、脉弦细")

    with col2:
        st.subheader("AI诊断结果")

        diagnose_clicked = st.button("🔍 开始诊断", type="primary", use_container_width=True)

        if diagnose_clicked:
            if not chief_complaint:
                st.error("请输入主诉信息")
            else:
                with st.spinner("AI正在分析中..."):
                    result = engine.analyze_symptoms(chief_complaint, selected_symptoms, tongue_sign, pulse_sign)

                st.session_state.last_result = result
                st.session_state.last_input = {
                    "name": patient_name or "匿名",
                    "age": patient_age,
                    "gender": patient_gender,
                    "chief_complaint": chief_complaint,
                    "symptoms": selected_symptoms,
                    "tongue_sign": tongue_sign,
                    "pulse_sign": pulse_sign,
                }

        if st.session_state.get("last_result"):
            result = st.session_state.last_result
            inp = st.session_state.get("last_input", {})

            if result["confidence"] > 0:
                st.success("诊断完成！")
            else:
                st.error(f"诊断异常：{result['syndrome']}")

            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("诊断证型", result["syndrome"])
                st.metric("辨证体系", result.get("syndrome_category", "待分类"))
            with col_b:
                st.metric("推荐方剂", result["formula"])
                st.metric("置信度", f"{result['confidence']}%")

            st.markdown("---")
            st.markdown("#### 辨证分析")
            st.info(result["analysis"])

            if result.get("treatment_principle") and result["treatment_principle"] != "无":
                st.markdown("#### 治疗原则")
                st.info(result["treatment_principle"])

            if result.get("formula") and result["formula"] not in ["无", "待推荐"]:
                st.markdown("#### 方剂")
                st.info(f"**{result['formula']}**")
                if result.get("formula_adjustment") and result["formula_adjustment"] != "无":
                    st.warning(f"**加减建议**：{result['formula_adjustment']}")

            if result.get("additional_notes"):
                st.markdown("#### 提示")
                st.warning(result["additional_notes"])

            if st.button("💾 保存此问诊记录", type="secondary", key="save_btn"):
                records = load_records()
                new_record = {
                    "id": len(records) + 1,
                    "name": inp.get("name", "匿名"),
                    "age": inp.get("age", 0),
                    "gender": inp.get("gender", ""),
                    "chief_complaint": inp.get("chief_complaint", ""),
                    "symptoms": inp.get("symptoms", []),
                    "tongue_sign": inp.get("tongue_sign", ""),
                    "pulse_sign": inp.get("pulse_sign", ""),
                    "syndrome": result["syndrome"],
                    "syndrome_category": result.get("syndrome_category", ""),
                    "formula": result["formula"],
                    "confidence": result["confidence"],
                    "analysis": result["analysis"],
                    "treatment_principle": result.get("treatment_principle", ""),
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                records.append(new_record)
                save_records(records)
                st.session_state.last_result = None
                st.session_state.last_input = None
                st.success("✅ 问诊记录已保存！点击「📊 数据分析」查看")
                st.rerun()
        else:
            st.info("👆 请填写左侧问诊信息，点击「开始诊断」查看结果")

def render_analytics_tab():
    st.markdown('<div class="section-header"><h2>📊 数据分析看板</h2></div>', unsafe_allow_html=True)

    records = load_records()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总问诊数", len(records))
    with col2:
        valid = [r for r in records if r.get("confidence", 0) > 0]
        st.metric("有效诊断", len(valid))
    with col3:
        avg_conf = sum(r.get("confidence", 0) for r in valid) / len(valid) if valid else 0
        st.metric("平均置信度", f"{avg_conf:.1f}%")
    with col4:
        if records:
            st.metric("最新记录", records[-1].get("date", "")[:10])
        else:
            st.metric("最新记录", "无")

    st.markdown("---")

    if not records:
        st.warning("📊 暂无问诊记录。请先在「📋 智能问诊」中诊断并保存记录。")
        return

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("证型分布")
        syndromes = [r["syndrome"] for r in records if r.get("confidence", 0) > 0]
        if syndromes:
            df = pd.DataFrame({"证型": syndromes}).value_counts().reset_index()
            df.columns = ["证型", "数量"]
            fig = px.pie(df, names="证型", values="数量")
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("辨证体系分布")
        cats = [r.get("syndrome_category", "") for r in records if r.get("syndrome_category")]
        if cats:
            df = pd.DataFrame({"辨证体系": cats}).value_counts().reset_index()
            df.columns = ["辨证体系", "数量"]
            fig = px.bar(df, x="辨证体系", y="数量", color="辨证体系")
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("问诊记录列表")
    df_list = pd.DataFrame([{
        "日期": r.get("date", "")[:10],
        "姓名": r.get("name", ""),
        "主诉": r.get("chief_complaint", "")[:25],
        "证型": r.get("syndrome", ""),
        "方剂": r.get("formula", ""),
        "置信度": f"{r.get('confidence', 0)}%"
    } for r in reversed(records)])
    st.dataframe(df_list, use_container_width=True)

def render_settings_tab():
    st.markdown('<div class="section-header"><h2>⚙️ 系统设置</h2></div>', unsafe_allow_html=True)

    settings = load_settings()

    st.subheader("API配置")

    provider_list = list(API_PROVIDERS.keys())
    current_provider = settings.get("provider", DEFAULT_PROVIDER)
    provider_idx = provider_list.index(current_provider) if current_provider in provider_list else 0

    col1, col2 = st.columns(2)
    with col1:
        provider = st.selectbox("选择 API 厂商", provider_list, index=provider_idx)
    with col2:
        provider_config = API_PROVIDERS[provider]
        models = provider_config["models"]
        current_model = settings.get("model", "") or provider_config["default_model"]
        model_idx = models.index(current_model) if current_model in models else 0
        model = st.selectbox("选择模型", models, index=model_idx)

    st.caption(f"📡 API 地址：{provider_config['base_url']}")

    current_key = settings.get("api_key", "")
    api_key = st.text_input("API Key", type="password", placeholder="输入你的 API Key（留空使用默认）", value=current_key if current_key != DEFAULT_API_KEY else "")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💾 保存配置", type="primary"):
            new_key = api_key if api_key and len(api_key) > 5 else DEFAULT_API_KEY
            new_settings = {
                "api_key": new_key,
                "provider": provider,
                "model": model
            }
            save_settings(new_settings)
            st.session_state.engine = TCMDiagnosisEngine(new_key, provider, model)
            st.session_state.engine_key = f"{provider}:{new_key}"
            st.success(f"✅ 配置已保存：{provider} / {model}")
            st.rerun()
    with col2:
        if st.button("🧪 测试连接"):
            test_key = api_key if api_key and len(api_key) > 5 else DEFAULT_API_KEY
            with st.spinner("测试中..."):
                test_engine = TCMDiagnosisEngine(test_key, provider, model)
                result = test_engine.analyze_symptoms("测试", [], "", "")
                if result.get("confidence", 0) > 0 or "失败" not in result.get("syndrome", ""):
                    st.success("✅ 连接成功！")
                else:
                    st.error(f"❌ {result.get('additional_notes', '连接失败')}")
    with col3:
        if st.button("🔄 恢复默认"):
            save_settings({"api_key": DEFAULT_API_KEY, "provider": DEFAULT_PROVIDER, "model": ""})
            st.session_state.engine = TCMDiagnosisEngine()
            st.session_state.engine_key = f"{DEFAULT_PROVIDER}:{DEFAULT_API_KEY}"
            st.success("✅ 已恢复默认配置")
            st.rerun()

    st.markdown("---")
    st.subheader("当前状态")
    st.success(f"🔑 当前使用：{settings.get('provider', DEFAULT_PROVIDER)} / {settings.get('model', '默认模型')}")
    st.caption("默认配置使用 DeepSeek API，其他用户无需配置即可使用")

    st.markdown("---")
    st.subheader("数据管理")
    records = load_records()
    st.info(f"📊 共 {len(records)} 条问诊记录")
    if st.button("🗑️ 清空所有记录"):
        save_records([])
        st.success("已清空")
        st.rerun()

def render_knowledge_tab():
    st.markdown('<div class="section-header"><h2>📚 中医知识库</h2></div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["方剂库", "证型库", "辨证体系"])

    with tab1:
        st.subheader("常用方剂")
        categories = list(set(f["category"] for f in FORMULAS))
        category_filter = st.selectbox("按类别筛选", ["全部"] + sorted(categories))

        filtered = FORMULAS if category_filter == "全部" else [f for f in FORMULAS if f["category"] == category_filter]

        for f in filtered:
            with st.expander(f"📜 {f['name']} [{f['category']}] - {f['source']}"):
                st.write(f"**组成**：{f['composition']}")
                st.write(f"**功效**：{f['function']}")
                st.write(f"**主治**：{f['indication']}")

    with tab2:
        st.subheader("证型分类")
        categories = list(set(s["category"] for s in SYNDROMES))
        category_filter = st.selectbox("按辨证体系筛选", ["全部"] + sorted(categories), key="syndrome_filter")

        filtered = SYNDROMES if category_filter == "全部" else [s for s in SYNDROMES if s["category"] == category_filter]

        for s in filtered:
            with st.expander(f"🩺 {s['name']} [{s['category']}]"):
                st.write(f"**主要症状**：{s['symptoms']}")
                st.write(f"**舌象**：{s['tongue']}")
                st.write(f"**脉象**：{s['pulse']}")
                st.write(f"**推荐方剂**：{s['formula']}")
                st.write(f"**治法**：{s['treatment']}")

    with tab3:
        st.subheader("辨证体系说明")
        st.markdown("""
        ### 六经辨证（《伤寒论》）
        - **太阳病**：表证，恶寒发热同时出现
        - **阳明病**：里实热证，但热不寒
        - **少阳病**：半表半里证，往来寒热
        - **太阴病**：里虚寒证，腹满吐利
        - **少阴病**：心肾阳虚或阴虚
        - **厥阴病**：寒热错杂，上热下寒

        ### 脏腑辨证
        - **心系**：心气虚、心血虚、心火亢盛、心血瘀阻
        - **肝系**：肝气郁结、肝火上炎、肝血虚、肝阳上亢
        - **脾系**：脾气虚、脾阳虚、脾不统血、寒湿困脾
        - **肺系**：肺气虚、肺阴虚、风寒犯肺、风热犯肺
        - **肾系**：肾阳虚、肾阴虚、肾精不足、肾不纳气

        ### 气血津液辨证
        - **气病**：气虚、气陷、气滞、气逆
        - **血病**：血虚、血瘀、血热、血寒
        - **津液病**：痰证、饮证、津亏证

        ### 辨证论治流程
        1. 四诊合参：望、闻、问、切
        2. 八纲辨证：表里、寒热、虚实、阴阳
        3. 脏腑辨证：定位到具体脏腑
        4. 确定证型：综合判断
        5. 确定治法：根据证型确定治疗原则
        6. 选方用药：根据治法选择方剂
        """)

def render_herb_tab():
    st.markdown('<div class="section-header"><h2>🌿 中药库</h2></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        search = st.text_input("🔍 搜索中药", placeholder="输入药名")
    with col2:
        natures = list(set(h["nature"] for h in HERBS))
        nature_filter = st.selectbox("按药性", ["全部"] + sorted(natures))
    with col3:
        flavors = list(set(h["flavor"] for h in HERBS))
        flavor_filter = st.selectbox("按药味", ["全部"] + sorted(flavors))

    filtered = HERBS
    if search:
        filtered = [h for h in filtered if search in h["name"]]
    if nature_filter != "全部":
        filtered = [h for h in filtered if h["nature"] == nature_filter]
    if flavor_filter != "全部":
        filtered = [h for h in filtered if flavor_filter in h["flavor"]]

    st.info(f"共找到 **{len(filtered)}** 味中药")

    for h in filtered:
        with st.expander(f"🌿 {h['name']} - {h['nature']}性 {h['flavor']}味"):
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"**药性**：{h['nature']}")
                st.write(f"**药味**：{h['flavor']}")
                st.write(f"**归经**：{h['meridian']}")
            with col_b:
                st.write(f"**功效**：{h['function']}")
                st.write(f"**主治**：{h['indication']}")
                st.write(f"**用量**：{h['dosage']}")
            if h.get("caution"):
                st.warning(f"**禁忌**：{h['caution']}")

if __name__ == "__main__":
    main()
