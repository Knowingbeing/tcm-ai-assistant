import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap');

    * {
        font-family: 'Noto Sans SC', sans-serif;
    }

    .stApp {
        background: linear-gradient(180deg, #F0F4F8 0%, #E2E8F0 100%);
    }

    .hero-section {
        background: linear-gradient(135deg, #0D7C66 0%, #0F9D58 50%, #10B981 100%);
        padding: 2.5rem 3rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(13, 124, 102, 0.3);
        position: relative;
        overflow: hidden;
    }

    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 400px;
        height: 400px;
        background: rgba(255,255,255,0.1);
        border-radius: 50%;
    }

    .hero-section::after {
        content: '';
        position: absolute;
        bottom: -30%;
        left: -10%;
        width: 300px;
        height: 300px;
        background: rgba(255,255,255,0.08);
        border-radius: 50%;
    }

    .hero-section h1 {
        color: white !important;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        position: relative;
        z-index: 1;
    }

    .hero-section .subtitle {
        color: rgba(255,255,255,0.95);
        margin: 0.8rem 0 0 0;
        font-size: 1.1rem;
        font-weight: 300;
        position: relative;
        z-index: 1;
    }

    .hero-section .badge {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin-top: 1rem;
        backdrop-filter: blur(10px);
        position: relative;
        z-index: 1;
    }

    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 1.5rem;
    }

    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        border: 1px solid rgba(0,0,0,0.04);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.12);
    }

    .stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #0D7C66 0%, #10B981 100%);
        border-radius: 0 4px 4px 0;
    }

    .stat-card .icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }

    .stat-card .value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1A1A2E;
        margin: 0;
    }

    .stat-card .label {
        font-size: 0.85rem;
        color: #64748B;
        margin: 0.3rem 0 0 0;
        font-weight: 500;
    }

    .section-container {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.04);
        border: 1px solid rgba(0,0,0,0.04);
    }

    .section-title {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin-bottom: 1.2rem;
        padding-bottom: 0.8rem;
        border-bottom: 2px solid #F1F5F9;
    }

    .section-title .icon-circle {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #0D7C66 0%, #10B981 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        box-shadow: 0 4px 12px rgba(13, 124, 102, 0.3);
    }

    .section-title h2 {
        margin: 0;
        font-size: 1.3rem;
        font-weight: 600;
        color: #1A1A2E;
    }

    .stButton>button {
        background: linear-gradient(135deg, #0D7C66 0%, #10B981 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.8rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(13, 124, 102, 0.3);
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(13, 124, 102, 0.4);
    }

    .stButton>button:active {
        transform: translateY(0);
    }

    div[data-testid="stMetric"] {
        background: white;
        padding: 1.2rem;
        border-radius: 14px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.04);
        border: 1px solid rgba(0,0,0,0.04);
        transition: all 0.3s;
    }

    div[data-testid="stMetric"]:hover {
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
    }

    div[data-testid="stMetric"] label {
        color: #64748B !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
    }

    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #1A1A2E !important;
        font-weight: 700 !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: #F1F5F9;
        padding: 6px;
        border-radius: 14px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 0.7rem 1.5rem;
        font-weight: 500;
        color: #64748B;
        background: transparent;
        border: none;
        transition: all 0.3s;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #0D7C66;
        background: rgba(13, 124, 102, 0.1);
    }

    .stTabs [aria-selected="true"] {
        background: white !important;
        color: #0D7C66 !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    }

    div[data-baseweb="tab-panel"] {
        padding: 1rem 0;
    }

    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 2px solid #E2E8F0;
        padding: 0.8rem 1rem;
        transition: all 0.3s;
    }

    .stTextInput>div>div>input:focus {
        border-color: #0D7C66;
        box-shadow: 0 0 0 3px rgba(13, 124, 102, 0.15);
    }

    .stTextArea>div>div>textarea {
        border-radius: 10px;
        border: 2px solid #E2E8F0;
        padding: 0.8rem 1rem;
        transition: all 0.3s;
    }

    .stTextArea>div>div>textarea:focus {
        border-color: #0D7C66;
        box-shadow: 0 0 0 3px rgba(13, 124, 102, 0.15);
    }

    .stSelectbox>div>div {
        border-radius: 10px;
    }

    .stMultiSelect>div>div {
        border-radius: 10px;
    }

    .stSuccess {
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
        border: 1px solid #6EE7B7;
        border-radius: 12px;
    }

    .stError {
        background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
        border: 1px solid #FCA5A5;
        border-radius: 12px;
    }

    .stWarning {
        background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
        border: 1px solid #FCD34D;
        border-radius: 12px;
    }

    .stInfo {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border: 1px solid #93C5FD;
        border-radius: 12px;
    }

    .expander {
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        overflow: hidden;
    }

    .expander-header {
        background: #F8FAFC;
        padding: 1rem;
        font-weight: 500;
    }

    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #E2E8F0, transparent);
        margin: 1.5rem 0;
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
    <div class="hero-section">
        <h1>🏥 中医AI智能问诊助手</h1>
        <p class="subtitle">基于大语言模型的中医智能辨证论治系统</p>
        <span class="badge">✨ 支持六经辨证 · 脏腑辨证 · 卫气营血辨证</span>
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
    st.markdown("""
    <div class="section-container">
        <div class="section-title">
            <div class="icon-circle">📋</div>
            <h2>智能问诊</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 3])

    with col1:
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.markdown("**👤 患者信息**")
        patient_name = st.text_input("姓名", placeholder="请输入患者姓名", label_visibility="collapsed")
        col_age, col_gender = st.columns(2)
        with col_age:
            patient_age = st.number_input("年龄", min_value=0, max_value=150, value=30)
        with col_gender:
            patient_gender = st.selectbox("性别", ["男", "女"])

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("**📝 问诊信息**")
        chief_complaint = st.text_area("主诉", placeholder="请描述主要症状，如：头痛、发热3天", height=120, label_visibility="collapsed")

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("**🔍 症状选择**")
        all_symptoms = ["发热", "恶寒", "畏寒", "头痛", "头晕", "咳嗽", "鼻塞", "流涕",
                       "咽喉痛", "胸闷", "心悸", "腹痛", "腹泻", "便秘", "食欲不振",
                       "口渴", "口苦", "失眠", "乏力", "自汗", "盗汗", "腰膝酸软",
                       "畏寒肢冷", "呕吐", "腹胀", "胸胁胀痛", "善太息", "情志抑郁",
                       "面红目赤", "急躁易怒", "眩晕", "耳鸣", "多梦", "健忘",
                       "气短", "神疲", "四肢厥冷", "干咳少痰", "痰多", "痰黄稠",
                       "关节疼痛", "身热不扬", "心烦", "消渴", "刺痛", "面色晦暗"]
        selected_symptoms = st.multiselect("选择伴随症状", all_symptoms, label_visibility="collapsed")

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("**👅 舌脉信息**")
        col_tongue, col_pulse = st.columns(2)
        with col_tongue:
            tongue_sign = st.text_input("舌象", placeholder="舌苔薄白")
        with col_pulse:
            pulse_sign = st.text_input("脉象", placeholder="脉浮紧")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.markdown("**🤖 AI诊断结果**")

        diagnose_clicked = st.button("🔍 开始诊断", type="primary", use_container_width=True)

        if diagnose_clicked:
            if not chief_complaint:
                st.error("⚠️ 请输入主诉信息")
            else:
                with st.spinner("🔄 AI正在分析中..."):
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
                st.success("✅ 诊断完成")
            else:
                st.error(f"❌ {result['syndrome']}")

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("🩺 诊断证型", result["syndrome"])
                st.metric("📚 辨证体系", result.get("syndrome_category", "待分类"))
            with col_b:
                st.metric("💊 推荐方剂", result["formula"])
                st.metric("📊 置信度", f"{result['confidence']}%")

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            st.markdown("**📖 辨证分析**")
            st.info(result["analysis"])

            if result.get("treatment_principle") and result["treatment_principle"] != "无":
                st.markdown("**🎯 治疗原则**")
                st.info(result["treatment_principle"])

            if result.get("formula") and result["formula"] not in ["无", "待推荐"]:
                st.markdown("**💊 方剂**")
                st.info(f"**{result['formula']}**")
                if result.get("formula_adjustment") and result["formula_adjustment"] != "无":
                    st.warning(f"**加减建议**：{result['formula_adjustment']}")

            if result.get("additional_notes"):
                st.markdown("**💡 提示**")
                st.warning(result["additional_notes"])

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            if st.button("💾 保存此问诊记录", type="primary", use_container_width=True, key="save_btn"):
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
            st.markdown("""
            <div style="text-align: center; padding: 3rem; color: #94A3B8;">
                <p style="font-size: 3rem; margin: 0;">🩺</p>
                <p style="font-size: 1.1rem; margin: 0.5rem 0;">请填写左侧问诊信息</p>
                <p style="font-size: 0.9rem;">点击「开始诊断」查看 AI 分析结果</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

def render_analytics_tab():
    st.markdown("""
    <div class="section-container">
        <div class="section-title">
            <div class="icon-circle">📊</div>
            <h2>数据分析看板</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)

    records = load_records()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📋 总问诊数", len(records))
    with col2:
        valid = [r for r in records if r.get("confidence", 0) > 0]
        st.metric("✅ 有效诊断", len(valid))
    with col3:
        avg_conf = sum(r.get("confidence", 0) for r in valid) / len(valid) if valid else 0
        st.metric("📊 平均置信度", f"{avg_conf:.1f}%")
    with col4:
        if records:
            st.metric("🕐 最新记录", records[-1].get("date", "")[:10])
        else:
            st.metric("🕐 最新记录", "无")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    if not records:
        st.markdown("""
        <div style="text-align: center; padding: 4rem; color: #94A3B8;">
            <p style="font-size: 4rem; margin: 0;">📊</p>
            <p style="font-size: 1.2rem; margin: 1rem 0;">暂无问诊记录</p>
            <p style="font-size: 0.95rem;">请先在「📋 智能问诊」中诊断并保存记录</p>
        </div>
        """, unsafe_allow_html=True)
        return

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.markdown("**🩺 证型分布**")
        syndromes = [r["syndrome"] for r in records if r.get("confidence", 0) > 0]
        if syndromes:
            df = pd.DataFrame({"证型": syndromes}).value_counts().reset_index()
            df.columns = ["证型", "数量"]
            fig = px.pie(df, names="证型", values="数量", color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=350)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.markdown("**📚 辨证体系分布**")
        cats = [r.get("syndrome_category", "") for r in records if r.get("syndrome_category")]
        if cats:
            df = pd.DataFrame({"辨证体系": cats}).value_counts().reset_index()
            df.columns = ["辨证体系", "数量"]
            fig = px.bar(df, x="辨证体系", y="数量", color="辨证体系",
                        color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=350, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown("**📋 问诊记录列表**")
    df_list = pd.DataFrame([{
        "日期": r.get("date", "")[:10],
        "姓名": r.get("name", ""),
        "主诉": r.get("chief_complaint", "")[:25],
        "证型": r.get("syndrome", ""),
        "方剂": r.get("formula", ""),
        "置信度": f"{r.get('confidence', 0)}%"
    } for r in reversed(records)])
    st.dataframe(df_list, use_container_width=True, height=300)
    st.markdown('</div>', unsafe_allow_html=True)

def render_knowledge_tab():
    st.markdown("""
    <div class="section-container">
        <div class="section-title">
            <div class="icon-circle">📚</div>
            <h2>中医知识库</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["💊 方剂库", "🩺 证型库", "📖 辨证体系"])

    with tab1:
        st.markdown('<div class="section-container">', unsafe_allow_html=True)

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search_formula = st.text_input("🔍 搜索方剂", placeholder="输入方剂名称...", key="formula_search", label_visibility="collapsed")
        with col2:
            categories = list(set(f["category"] for f in FORMULAS))
            category_filter = st.selectbox("按类别", ["全部"] + sorted(categories), key="formula_category")
        with col3:
            sources = list(set(f["source"] for f in FORMULAS))
            source_filter = st.selectbox("按来源", ["全部"] + sorted(sources), key="formula_source")

        filtered = FORMULAS
        if search_formula:
            filtered = [f for f in filtered if search_formula in f["name"] or search_formula in f["composition"]]
        if category_filter != "全部":
            filtered = [f for f in filtered if f["category"] == category_filter]
        if source_filter != "全部":
            filtered = [f for f in filtered if f["source"] == source_filter]

        st.markdown(f"共找到 **{len(filtered)}** 个方剂")
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        for f in filtered:
            with st.expander(f"📜 **{f['name']}** [{f['category']}] - {f['source']}"):
                col_a, col_b = st.columns([1, 1])
                with col_a:
                    st.markdown(f"**💊 组成**：{f['composition']}")
                    st.markdown(f"**🎯 功效**：{f['function']}")
                with col_b:
                    st.markdown(f"**📋 主治**：{f['indication']}")
                    st.markdown(f"**📖 来源**：{f['source']}")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="section-container">', unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])
        with col1:
            search_syndrome = st.text_input("🔍 搜索证型", placeholder="输入证型名称或症状...", key="syndrome_search", label_visibility="collapsed")
        with col2:
            categories = list(set(s["category"] for s in SYNDROMES))
            category_filter = st.selectbox("按辨证体系", ["全部"] + sorted(categories), key="syndrome_category")

        filtered = SYNDROMES
        if search_syndrome:
            filtered = [s for s in filtered if search_syndrome in s["name"] or search_syndrome in s["symptoms"]]
        if category_filter != "全部":
            filtered = [s for s in filtered if s["category"] == category_filter]

        st.markdown(f"共找到 **{len(filtered)}** 个证型")
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        for s in filtered:
            with st.expander(f"🩺 **{s['name']}** [{s['category']}]"):
                col_a, col_b = st.columns([1, 1])
                with col_a:
                    st.markdown(f"**🔍 主要症状**：{s['symptoms']}")
                    st.markdown(f"**👅 舌象**：{s['tongue']}")
                    st.markdown(f"**🤚 脉象**：{s['pulse']}")
                with col_b:
                    st.markdown(f"**💊 推荐方剂**：{s['formula']}")
                    st.markdown(f"**🎯 治法**：{s['treatment']}")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.markdown("**📖 辨证体系说明**")
        st.markdown("""
        ### 🔄 六经辨证（《伤寒论》）

        六经辨证是《伤寒论》的核心辨证体系，将外感热病分为六个阶段：

        | 经络 | 证型 | 主要表现 | 代表方剂 | 病机 |
        |------|------|----------|----------|------|
        | 太阳 | 表证 | 恶寒发热、头痛身痛 | 麻黄汤、桂枝汤 | 风寒袭表 |
        | 阳明 | 里实热证 | 但热不寒、大汗大渴 | 白虎汤、承气汤 | 里热炽盛 |
        | 少阳 | 半表半里证 | 往来寒热、口苦咽干 | 小柴胡汤 | 枢机不利 |
        | 太阴 | 里虚寒证 | 腹满吐利、喜温喜按 | 理中丸 | 脾阳不振 |
        | 少阴 | 心肾虚证 | 畏寒蜷卧或心烦不得眠 | 四逆汤、黄连阿胶汤 | 心肾阳虚/阴虚 |
        | 厥阴 | 寒热错杂 | 消渴、气上撞心 | 乌梅丸 | 阴阳对峙 |

        ### 🏥 脏腑辨证

        脏腑辨证是根据脏腑的生理功能和病理特点，对疾病进行辨证的方法：

        - **心系**：心气虚、心血虚、心火亢盛、心血瘀阻
        - **肝系**：肝气郁结、肝火上炎、肝血虚、肝阳上亢
        - **脾系**：脾气虚、脾阳虚、脾不统血、寒湿困脾、湿热蕴脾
        - **肺系**：肺气虚、肺阴虚、风寒犯肺、风热犯肺、痰热壅肺
        - **肾系**：肾阳虚、肾阴虚、肾精不足、肾不纳气

        ### 🩸 气血津液辨证

        - **气病**：气虚、气陷、气滞、气逆
        - **血病**：血虚、血瘀、血热、血寒
        - **津液病**：痰证、饮证、津亏证

        ### 🌡️ 卫气营血辨证（温病学）

        卫气营血辨证是温病学的核心辨证体系：

        | 分期 | 病位 | 主要表现 | 治法 | 代表方剂 |
        |------|------|----------|------|----------|
        | 卫分 | 肌表 | 发热微恶风寒 | 辛凉解表 | 银翘散 |
        | 气分 | 脏腑 | 壮热不恶寒 | 清气泄热 | 白虎汤 |
        | 营分 | 营阴 | 身热夜甚、心烦 | 清营透热 | 清营汤 |
        | 血分 | 血分 | 出血、发斑 | 凉血散血 | 犀角地黄汤 |

        ### 📝 辨证论治流程

        1. **四诊合参**：望、闻、问、切收集病情资料
        2. **八纲辨证**：确定表里、寒热、虚实、阴阳
        3. **脏腑辨证**：定位到具体脏腑
        4. **确定证型**：综合判断，确定证型
        5. **确定治法**：根据证型确定治疗原则
        6. **选方用药**：根据治法选择方剂，随证加减
        """)
        st.markdown('</div>', unsafe_allow_html=True)

def render_herb_tab():
    st.markdown("""
    <div class="section-container">
        <div class="section-title">
            <div class="icon-circle">🌿</div>
            <h2>中药库</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        search = st.text_input("🔍 搜索中药", placeholder="输入药名搜索...", label_visibility="collapsed")
    with col2:
        natures = sorted(list(set(h["nature"] for h in HERBS)))
        nature_filter = st.selectbox("药性", ["全部"] + natures)
    with col3:
        flavors = sorted(list(set(h["flavor"] for h in HERBS)))
        flavor_filter = st.selectbox("药味", ["全部"] + flavors)
    with col4:
        meridians = sorted(list(set(h["meridian"] for h in HERBS)))
        meridian_filter = st.selectbox("归经", ["全部"] + meridians)

    filtered = HERBS
    if search:
        filtered = [h for h in filtered if search in h["name"]]
    if nature_filter != "全部":
        filtered = [h for h in filtered if h["nature"] == nature_filter]
    if flavor_filter != "全部":
        filtered = [h for h in filtered if flavor_filter in h["flavor"]]
    if meridian_filter != "全部":
        filtered = [h for h in filtered if meridian_filter in h["meridian"]]

    st.markdown(f"共找到 **{len(filtered)}** 味中药")
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    for h in filtered:
        with st.expander(f"🌿 **{h['name']}** - {h['nature']}性 {h['flavor']}味 | {h['meridian']}"):
            col_a, col_b = st.columns([1, 1])
            with col_a:
                st.markdown(f"**🌡️ 药性**：{h['nature']}")
                st.markdown(f"**👅 药味**：{h['flavor']}")
                st.markdown(f"**📍 归经**：{h['meridian']}")
                st.markdown(f"**📏 用量**：{h['dosage']}")
            with col_b:
                st.markdown(f"**🎯 功效**：{h['function']}")
                st.markdown(f"**📋 主治**：{h['indication']}")
            if h.get("caution"):
                st.warning(f"**⚠️ 禁忌**：{h['caution']}")

def render_settings_tab():
    st.markdown("""
    <div class="section-container">
        <div class="section-title">
            <div class="icon-circle">⚙️</div>
            <h2>系统设置</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)

    settings = load_settings()

    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown("**🔑 API配置**")

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
        if st.button("💾 保存配置", type="primary", use_container_width=True):
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
        if st.button("🧪 测试连接", use_container_width=True):
            test_key = api_key if api_key and len(api_key) > 5 else DEFAULT_API_KEY
            with st.spinner("测试中..."):
                test_engine = TCMDiagnosisEngine(test_key, provider, model)
                result = test_engine.analyze_symptoms("测试", [], "", "")
                if result.get("confidence", 0) > 0 or "失败" not in result.get("syndrome", ""):
                    st.success("✅ 连接成功！")
                else:
                    st.error(f"❌ {result.get('additional_notes', '连接失败')}")
    with col3:
        if st.button("🔄 恢复默认", use_container_width=True):
            save_settings({"api_key": DEFAULT_API_KEY, "provider": DEFAULT_PROVIDER, "model": ""})
            st.session_state.engine = TCMDiagnosisEngine()
            st.session_state.engine_key = f"{DEFAULT_PROVIDER}:{DEFAULT_API_KEY}"
            st.success("✅ 已恢复默认配置")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown("**📊 当前状态**")
    st.success(f"🔑 当前使用：{settings.get('provider', DEFAULT_PROVIDER)} / {settings.get('model', '默认模型')}")
    st.caption("默认配置使用 DeepSeek API，其他用户无需配置即可使用")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown("**🗄️ 数据管理**")
    records = load_records()
    st.info(f"📊 共 {len(records)} 条问诊记录")
    if st.button("🗑️ 清空所有记录", use_container_width=True):
        save_records([])
        st.success("已清空")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
