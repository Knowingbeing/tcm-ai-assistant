"""
中医AI智能问诊助手 - 主应用
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
from datetime import datetime
from typing import Dict, List
import sys

sys.path.append(os.path.dirname(__file__))
from utils.llm_engine import TCMDiagnosisEngine, API_PROVIDERS, DEFAULT_API_KEY, DEFAULT_PROVIDER
from utils.supabase_client import (
    is_configured as supabase_configured,
    get_records as _sb_get_records,
    save_record as _sb_save_record,
    clear_records as _sb_clear_records,
    get_settings as _sb_get_settings,
    save_settings as _sb_save_settings,
)
from data.tcm_data import FORMULAS, SYNDROMES, HERBS
from data.ten_asks import TEN_ASKS, MENSTRUATION_ASK, TONGUE_ASK, PULSE_ASK, DEFAULT_TEN_ASKS

st.set_page_config(
    page_title="中医AI智能问诊助手",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== CSS 样式 ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap');
    * { font-family: 'Noto Sans SC', sans-serif; }
    .stApp { background: linear-gradient(180deg, #F0F4F8 0%, #E2E8F0 100%); }
    .hero-section {
        background: linear-gradient(135deg, #0D7C66 0%, #0F9D58 50%, #10B981 100%);
        padding: 2rem 3rem; border-radius: 16px; color: white; margin-bottom: 1.5rem;
        box-shadow: 0 15px 50px rgba(13, 124, 102, 0.25);
    }
    .hero-section h1 { color: white !important; margin: 0; font-size: 2rem; font-weight: 700; }
    .hero-section .subtitle { color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1rem; }
    .hero-section .badge {
        display: inline-block; background: rgba(255,255,255,0.2);
        padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.85rem;
        margin-top: 0.8rem; backdrop-filter: blur(10px);
    }
    .card {
        background: white; border-radius: 14px; padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.04); border: 1px solid rgba(0,0,0,0.04);
        margin-bottom: 1rem;
    }
    .card-title {
        display: flex; align-items: center; gap: 0.6rem;
        font-size: 1.1rem; font-weight: 600; color: #1A1A2E; margin-bottom: 0.8rem;
    }
    .card-title .ti {
        width: 32px; height: 32px; background: linear-gradient(135deg, #0D7C66 0%, #10B981 100%);
        border-radius: 8px; display: flex; align-items: center; justify-content: center;
        font-size: 1rem; color: white;
    }
    .divider { height: 1px; background: linear-gradient(90deg, transparent, #E2E8F0, transparent); margin: 1rem 0; }
    .stButton>button {
        background: linear-gradient(135deg, #0D7C66 0%, #10B981 100%); color: white;
        border: none; border-radius: 10px; padding: 0.6rem 1.5rem; font-weight: 600;
        box-shadow: 0 4px 15px rgba(13, 124, 102, 0.3); transition: all 0.3s;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(13, 124, 102, 0.4); }
    .result-card {
        background: white; border-radius: 12px; padding: 1rem; margin-bottom: 0.8rem;
        border-left: 3px solid #0D7C66; box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .result-card .head { font-weight: 600; color: #1A1A2E; margin-bottom: 0.5rem; }
    .result-card .body { color: #4A5568; font-size: 0.95rem; line-height: 1.6; }
    .result-hero {
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
        border-radius: 14px; padding: 1.2rem; margin-bottom: 1rem;
    }
    .result-hero.fail { background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%); }
    .confidence-bar {
        height: 6px; background: #E2E8F0; border-radius: 3px; margin-top: 0.3rem;
    }
    .confidence-bar .fill {
        height: 100%; background: linear-gradient(90deg, #0D7C66, #10B981);
        border-radius: 3px; transition: width 0.5s;
    }
    .stage-header {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        padding: 0.8rem 1rem; border-radius: 10px; margin-bottom: 0.8rem;
        border-left: 4px solid #0D7C66;
    }
    .stage-header h3 { margin: 0; font-size: 1rem; color: #1B5E20; }
</style>
""", unsafe_allow_html=True)

# ==================== 数据存储函数 ====================
DATA_DIR = "/tmp" if os.path.exists("/tmp") else "data"
os.makedirs(DATA_DIR, exist_ok=True)
RECORDS_FILE = os.path.join(DATA_DIR, "tcm_records.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "tcm_settings.json")

def load_records():
    if supabase_configured():
        rows = _sb_get_records()
        return [_row_to_record(r) for r in rows]
    if os.path.exists(RECORDS_FILE):
        try:
            with open(RECORDS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def _row_to_record(row: Dict) -> Dict:
    return {
        "id": row.get("id"), "name": row.get("name", "匿名"),
        "age": row.get("age", 0) or 0, "gender": row.get("gender", ""),
        "chief_complaint": row.get("chief_complaint", ""),
        "symptoms": row.get("symptoms", []) or [],
        "tongue_sign": row.get("tongue_sign", ""),
        "pulse_sign": row.get("pulse_sign", ""),
        "syndrome": row.get("syndrome", "待辨证"),
        "syndrome_category": row.get("syndrome_category", ""),
        "formula": row.get("formula", "待推荐"),
        "formula_adjustment": row.get("formula_adjustment", ""),
        "treatment_principle": row.get("treatment_principle", ""),
        "analysis": row.get("analysis", ""),
        "confidence": row.get("confidence", 0) or 0,
        "date": row.get("created_at", ""),
    }

def save_records(records):
    if supabase_configured():
        if records:
            _sb_save_record(records[-1])
        return
    with open(RECORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

def load_settings():
    if supabase_configured():
        return _sb_get_settings()
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"api_key": DEFAULT_API_KEY, "provider": DEFAULT_PROVIDER, "model": ""}

def save_settings(settings):
    if supabase_configured():
        _sb_save_settings(settings)
        return
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

# ==================== 主函数 ====================
def main():
    engine = get_engine()
    settings = load_settings()
    has_api_key = bool(settings.get("api_key", ""))

    st.markdown("""
    <div class="hero-section">
        <h1>🏥 中医AI智能问诊助手</h1>
        <p class="subtitle">基于大语言模型的中医智能辨证论治系统</p>
        <span class="badge">✨ 十问歌结构化问诊 · 六经/脏腑/卫气营血辨证</span>
    </div>
    """, unsafe_allow_html=True)

    if not has_api_key:
        st.warning("⚠️ **请先配置 API Key**：前往「⚙️ 系统设置」页面输入你的 API Key，才能使用 AI 智能诊断功能。")

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

# ==================== 智能问诊 Tab ====================
def render_consultation_tab(engine):
    """十问歌结构化问诊"""

    if "consultation" not in st.session_state:
        st.session_state.consultation = {
            "patient": {"name": "匿名", "age": 30, "gender": "男"},
            "chief_complaint": "",
            "ten_asks": dict(DEFAULT_TEN_ASKS),
            "tongue_sign": "",
            "pulse_sign": "",
            "result": None,
            "saved": False,
        }
    sess = st.session_state.consultation

    st.markdown("""
    <div class="card">
        <div class="card-title"><div class="ti">📋</div>十问歌智能问诊</div>
        <p style="color:#64748B; margin:0; font-size:0.9rem;">
            按照中医十问歌逐项填写，AI 将根据你的回答进行辨证论治。
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        # 患者信息
        st.markdown("""
        <div class="card-title"><div class="ti">👤</div>患者信息</div>
        """, unsafe_allow_html=True)
        sess["patient"]["name"] = st.text_input("姓名", value=sess["patient"].get("name", "匿名"), placeholder="可选", key="p_name")
        c1, c2 = st.columns(2)
        with c1:
            sess["patient"]["age"] = st.number_input("年龄", min_value=0, max_value=150, value=int(sess["patient"].get("age", 30)), key="p_age")
        with c2:
            sess["patient"]["gender"] = st.selectbox("性别", ["男", "女"], index=0 if sess["patient"].get("gender", "男") == "男" else 1, key="p_gender")

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # 主诉
        st.markdown("""
        <div class="card-title"><div class="ti">📝</div>主诉</div>
        """, unsafe_allow_html=True)
        sess["chief_complaint"] = st.text_area("主诉", value=sess.get("chief_complaint", ""), placeholder="请简要描述您的主要不适，如：头痛3天、怕冷、不出汗", height=80, key="chief")

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # 十问歌
        st.markdown("""
        <div class="card-title"><div class="ti">📋</div>十问歌</div>
        """, unsafe_allow_html=True)

        for stage in [1, 2, 3]:
            stage_asks = [ask for ask in TEN_ASKS if ask.get("stage") == stage]
            if stage_asks:
                with st.expander(f"📌 第{stage}阶段", expanded=(stage == 1)):
                    for ask in stage_asks:
                        key = ask["key"]
                        label = f"{ask['icon']} {ask['label']}"

                        if ask.get("input_type") == "text":
                            sess["ten_asks"][key] = st.text_input(label, value=sess["ten_asks"].get(key, ""), placeholder=ask.get("placeholder", ""), key=f"t_{key}")
                        elif ask.get("multi"):
                            current = sess["ten_asks"].get(key, {})
                            if isinstance(current, dict):
                                current = current.get("parts", [])
                            selected = st.multiselect(label, ask["options"], default=[s for s in current if s in ask["options"]], key=f"t_{key}")
                            sess["ten_asks"][key] = {"parts": selected, "detail": ""}
                        elif "sub_asks" in ask:
                            sub_data = sess["ten_asks"].get(key, {})
                            if not isinstance(sub_data, dict):
                                sub_data = {}
                            cols = st.columns(len(ask["sub_asks"]))
                            for i, sub in enumerate(ask["sub_asks"]):
                                with cols[i]:
                                    val = st.selectbox(f"{ask['label']}-{sub['label']}", sub["options"], index=sub["options"].index(sub_data.get(sub["key"], sub["options"][0])) if sub_data.get(sub["key"]) in sub["options"] else 0, key=f"t_{key}_{sub['key']}")
                                    sub_data[sub["key"]] = val
                            sess["ten_asks"][key] = sub_data
                        else:
                            options = ["请选择"] + ask["options"]
                            current_val = sess["ten_asks"].get(key, {})
                            if isinstance(current_val, dict):
                                current_val = current_val.get("type", "")
                            idx = options.index(current_val) if current_val in options else 0
                            selected = st.selectbox(label, options, index=idx, key=f"t_{key}")
                            sess["ten_asks"][key] = {"type": selected if selected != "请选择" else "", "detail": ""}

        # 女性经期
        if sess["patient"].get("gender") == "女":
            with st.expander("🌸 经期问诊", expanded=False):
                menstruation = sess["ten_asks"].get("menstruation") or {}
                cols = st.columns(4)
                for i, sub in enumerate(MENSTRUATION_ASK["sub_asks"]):
                    with cols[i]:
                        val = st.selectbox(f"月经{sub['label']}", sub["options"], index=sub["options"].index(menstruation.get(sub["key"], sub["options"][0])) if menstruation.get(sub["key"]) in sub["options"] else 0, key=f"t_m_{sub['key']}")
                        menstruation[sub["key"]] = val
                sess["ten_asks"]["menstruation"] = menstruation

        # 舌脉
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            sess["tongue_sign"] = st.text_input("👅 舌象", value=sess.get("tongue_sign", ""), placeholder=TONGUE_ASK.get("placeholder", ""), key="tongue")
        with c2:
            pulse_options = ["请选择"] + PULSE_ASK["options"]
            current_pulse = sess.get("pulse_sign", "")
            idx = pulse_options.index(current_pulse) if current_pulse in pulse_options else 0
            selected_pulse = st.selectbox("🫀 脉象", pulse_options, index=idx, key="pulse")
            sess["pulse_sign"] = selected_pulse if selected_pulse != "请选择" else ""

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("""
        <div class="card-title"><div class="ti">🩺</div>诊断结果</div>
        """, unsafe_allow_html=True)

        if sess.get("result"):
            result = sess["result"]
            is_ok = result.get("confidence", 0) > 0
            conf = result.get("confidence", 0)

            st.markdown(f"""
            <div class="result-hero{'fail' if not is_ok else ''}">
                <div style="font-weight:600; color:#1B5E20;">{'✅ 辨证完成' if is_ok else '❌ 辨证失败'}</div>
                <div style="font-size:1.5rem; font-weight:700; margin:0.5rem 0;">🩺 {result.get('syndrome', '')}</div>
                <div style="display:flex; gap:2rem;">
                    <div><span style="color:#64748B;">辨证体系</span><br><b>{result.get('syndrome_category', '待分类')}</b></div>
                    <div><span style="color:#64748B;">置信度</span><br><b>{conf}%</b>
                        <div class="confidence-bar"><div class="fill" style="width:{min(conf, 100)}%"></div></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if result.get("analysis"):
                st.markdown(f"""<div class="result-card"><div class="head">📖 辨证分析</div><div class="body">{result['analysis']}</div></div>""", unsafe_allow_html=True)
            if result.get("treatment_principle") and result["treatment_principle"] not in ("无", ""):
                st.markdown(f"""<div class="result-card"><div class="head">🎯 治疗原则</div><div class="body">{result['treatment_principle']}</div></div>""", unsafe_allow_html=True)
            if result.get("formula") and result["formula"] not in ("无", "待推荐"):
                st.markdown(f"""<div class="result-card"><div class="head">💊 推荐方剂</div><div class="body" style="font-size:1.1rem; font-weight:600;">{result['formula']}</div></div>""", unsafe_allow_html=True)
            if result.get("formula_adjustment") and result["formula_adjustment"] not in ("无", ""):
                st.markdown(f"""<div class="result-card" style="border-left-color:#F59E0B;"><div class="head" style="color:#92400E;">🧩 加减建议</div><div class="body">{result['formula_adjustment']}</div></div>""", unsafe_allow_html=True)
            if result.get("additional_notes") and result["additional_notes"] not in ("无", ""):
                st.markdown(f"""<div class="result-card" style="border-left-color:#EF4444;"><div class="head" style="color:#991B1B;">💡 提示</div><div class="body">{result['additional_notes']}</div></div>""", unsafe_allow_html=True)

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if sess.get("saved"):
                    st.success("✅ 已保存")
                else:
                    if st.button("💾 保存此次问诊", type="primary", use_container_width=True):
                        _save_consultation(sess)
                        st.success("✅ 已保存！")
            with c2:
                if st.button("🔄 重新问诊", use_container_width=True):
                    st.session_state.consultation = {"patient": {"name": "匿名", "age": 30, "gender": "男"}, "chief_complaint": "", "ten_asks": dict(DEFAULT_TEN_ASKS), "tongue_sign": "", "pulse_sign": "", "result": None, "saved": False}
                    st.rerun()
        else:
            st.info("👈 请在左侧填写十问歌信息后，点击「开始诊断」")

            if st.button("🔍 开始诊断", type="primary", use_container_width=True):
                _run_diagnosis(sess, engine)
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

def _collect_symptoms(sess):
    """从十问歌数据中收集症状"""
    symptoms = []
    ten = sess.get("ten_asks", {})
    for key, val in ten.items():
        if isinstance(val, dict):
            if "parts" in val:
                symptoms.extend([p for p in val.get("parts", []) if p and p != "无不适"])
            elif "type" in val and val["type"] and val["type"] != "请选择":
                symptoms.append(val["type"])
            elif "stool" in val and val.get("stool") and val["stool"] != "正常":
                symptoms.append(f"大便{val['stool']}")
            elif "urine" in val and val.get("urine") and val["urine"] != "正常":
                symptoms.append(f"小便{val['urine']}")
            elif "appetite" in val and val.get("appetite") and val["appetite"] != "正常":
                symptoms.append(val["appetite"])
            elif "thirst" in val and val.get("thirst") and val["thirst"] != "正常":
                symptoms.append(val["thirst"])
            elif "quality" in val and val.get("quality") and val["quality"] != "正常":
                symptoms.append(val["quality"])
        elif isinstance(val, str) and val:
            symptoms.append(val)
    return list(set(symptoms))

def _run_diagnosis(sess, engine):
    """运行诊断"""
    if not sess.get("chief_complaint", "").strip():
        st.toast("⚠️ 请先填写主诉", icon="⚠️")
        return

    symptoms = _collect_symptoms(sess)
    result = engine.analyze_symptoms(
        sess["chief_complaint"], symptoms,
        sess.get("tongue_sign", ""), sess.get("pulse_sign", ""),
    )
    sess["result"] = result
    sess["saved"] = False

def _save_consultation(sess):
    """保存问诊记录"""
    symptoms = _collect_symptoms(sess)
    record = {
        "name": sess["patient"].get("name", "匿名"),
        "age": sess["patient"].get("age", 0),
        "gender": sess["patient"].get("gender", ""),
        "chief_complaint": sess.get("chief_complaint", ""),
        "symptoms": symptoms,
        "tongue_sign": sess.get("tongue_sign", ""),
        "pulse_sign": sess.get("pulse_sign", ""),
        "syndrome": sess["result"].get("syndrome", ""),
        "syndrome_category": sess["result"].get("syndrome_category", ""),
        "formula": sess["result"].get("formula", ""),
        "formula_adjustment": sess["result"].get("formula_adjustment", ""),
        "treatment_principle": sess["result"].get("treatment_principle", ""),
        "analysis": sess["result"].get("analysis", ""),
        "confidence": sess["result"].get("confidence", 0),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    if supabase_configured():
        _sb_save_record(record)
    else:
        records = load_records()
        record["id"] = len(records) + 1
        records.append(record)
        save_records(records)
    sess["saved"] = True

# ==================== 数据分析 Tab ====================
def render_analytics_tab():
    st.markdown("""
    <div class="card">
        <div class="card-title"><div class="ti">📊</div>数据分析看板</div>
    </div>
    """, unsafe_allow_html=True)

    records = load_records()
    valid = [r for r in records if r.get("confidence", 0) > 0]
    avg_conf = sum(r.get("confidence", 0) for r in valid) / len(valid) if valid else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("📋 总问诊数", len(records))
    with col2: st.metric("✅ 有效诊断", len(valid))
    with col3: st.metric("📊 平均置信度", f"{avg_conf:.1f}%")
    with col4:
        last_date = records[-1].get("date", "")[:10] if records else "无"
        st.metric("🕐 最新记录", last_date)

    if not records:
        st.info("📊 暂无问诊记录，请先在「📋 智能问诊」中诊断并保存记录。")
        return

    col_left, col_right = st.columns(2)
    with col_left:
        syndromes = [r["syndrome"] for r in valid]
        if syndromes:
            df = pd.DataFrame({"证型": syndromes}).value_counts().reset_index()
            df.columns = ["证型", "数量"]
            fig = px.pie(df, names="证型", values="数量", color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
    with col_right:
        cats = [r.get("syndrome_category", "") for r in valid if r.get("syndrome_category")]
        if cats:
            df = pd.DataFrame({"辨证体系": cats}).value_counts().reset_index()
            df.columns = ["辨证体系", "数量"]
            fig = px.bar(df, x="辨证体系", y="数量", color="辨证体系", color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig, use_container_width=True)

# ==================== 知识库 Tab ====================
def render_knowledge_tab():
    st.markdown("""
    <div class="card">
        <div class="card-title"><div class="ti">📚</div>中医知识库</div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["💊 方剂库", "🩺 证型库", "📖 辨证体系"])

    with tab1:
        search = st.text_input("🔍 搜索方剂", placeholder="输入方剂名称...", key="f_search")
        categories = list(set(f["category"] for f in FORMULAS))
        cat_filter = st.selectbox("按类别", ["全部"] + sorted(categories), key="f_cat")
        filtered = FORMULAS
        if search: filtered = [f for f in filtered if search in f["name"] or search in f["composition"]]
        if cat_filter != "全部": filtered = [f for f in filtered if f["category"] == cat_filter]
        st.caption(f"共 {len(filtered)} 个方剂")
        for f in filtered:
            with st.expander(f"📜 **{f['name']}** [{f['category']}]"):
                st.markdown(f"**💊 组成**：{f['composition']}")
                st.markdown(f"**🎯 功效**：{f['function']}")
                st.markdown(f"**📋 主治**：{f['indication']}")

    with tab2:
        search = st.text_input("🔍 搜索证型", placeholder="输入证型名称...", key="s_search")
        categories = list(set(s["category"] for s in SYNDROMES))
        cat_filter = st.selectbox("按辨证体系", ["全部"] + sorted(categories), key="s_cat")
        filtered = SYNDROMES
        if search: filtered = [s for s in filtered if search in s["name"] or search in s["symptoms"]]
        if cat_filter != "全部": filtered = [s for s in filtered if s["category"] == cat_filter]
        st.caption(f"共 {len(filtered)} 个证型")
        for s in filtered:
            with st.expander(f"🩺 **{s['name']}** [{s['category']}]"):
                st.markdown(f"**🔍 主要症状**：{s['symptoms']}")
                st.markdown(f"**👅 舌象**：{s['tongue']} | **🤚 脉象**：{s['pulse']}")
                st.markdown(f"**💊 推荐方剂**：{s['formula']} | **🎯 治法**：{s['treatment']}")

    with tab3:
        st.markdown("""
        ### 🔄 六经辨证（《伤寒论》）
        | 经络 | 证型 | 主要表现 | 代表方剂 |
        |------|------|----------|----------|
        | 太阳 | 表证 | 恶寒发热、头痛身痛 | 麻黄汤、桂枝汤 |
        | 阳明 | 里实热证 | 但热不寒、大汗大渴 | 白虎汤、承气汤 |
        | 少阳 | 半表半里证 | 往来寒热、口苦咽干 | 小柴胡汤 |
        | 太阴 | 里虚寒证 | 腹满吐利、喜温喜按 | 理中丸 |
        | 少阴 | 心肾虚证 | 畏寒蜷卧或心烦不得眠 | 四逆汤 |
        | 厥阴 | 寒热错杂 | 消渴、气上撞心 | 乌梅丸 |

        ### 🏥 脏腑辨证
        - **心系**：心气虚、心血虚、心火亢盛、心血瘀阻
        - **肝系**：肝气郁结、肝火上炎、肝血虚、肝阳上亢
        - **脾系**：脾气虚、脾阳虚、脾不统血、寒湿困脾、湿热蕴脾
        - **肺系**：肺气虚、肺阴虚、风寒犯肺、风热犯肺、痰热壅肺
        - **肾系**：肾阳虚、肾阴虚、肾精不足、肾不纳气

        ### 🩸 气血津液辨证
        - **气病**：气虚、气陷、气滞、气逆
        - **血病**：血虚、血瘀、血热、血寒
        - **津液病**：痰证、饮证、津亏证
        """)

# ==================== 中药库 Tab ====================
def render_herb_tab():
    st.markdown("""
    <div class="card">
        <div class="card-title"><div class="ti">🌿</div>中药库</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1: search = st.text_input("🔍 搜索中药", placeholder="输入药名...", key="h_search", label_visibility="collapsed")
    with col2: natures = sorted(list(set(h["nature"] for h in HERBS))); nature_filter = st.selectbox("药性", ["全部"] + natures, key="h_nature")
    with col3: flavors = sorted(list(set(h["flavor"] for h in HERBS))); flavor_filter = st.selectbox("药味", ["全部"] + flavors, key="h_flavor")
    with col4: meridians = sorted(list(set(h["meridian"] for h in HERBS))); meridian_filter = st.selectbox("归经", ["全部"] + meridians, key="h_meridian")

    filtered = HERBS
    if search: filtered = [h for h in filtered if search in h["name"]]
    if nature_filter != "全部": filtered = [h for h in filtered if h["nature"] == nature_filter]
    if flavor_filter != "全部": filtered = [h for h in filtered if flavor_filter in h["flavor"]]
    if meridian_filter != "全部": filtered = [h for h in filtered if meridian_filter in h["meridian"]]

    st.caption(f"共 {len(filtered)} 味中药")
    for h in filtered:
        with st.expander(f"🌿 **{h['name']}** - {h['nature']}性 {h['flavor']}味 | {h['meridian']}"):
            st.markdown(f"**🌡️ 药性**：{h['nature']} | **👅 药味**：{h['flavor']} | **📍 归经**：{h['meridian']} | **📏 用量**：{h['dosage']}")
            st.markdown(f"**🎯 功效**：{h['function']}")
            st.markdown(f"**📋 主治**：{h['indication']}")
            if h.get("caution"): st.warning(f"**⚠️ 禁忌**：{h['caution']}")

# ==================== 系统设置 Tab ====================
def render_settings_tab():
    st.markdown("""
    <div class="card">
        <div class="card-title"><div class="ti">⚙️</div>系统设置</div>
    </div>
    """, unsafe_allow_html=True)

    settings = load_settings()
    current_key = settings.get("api_key", "")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**🔑 API配置**")

    provider_list = list(API_PROVIDERS.keys())
    provider_idx = provider_list.index(settings.get("provider", DEFAULT_PROVIDER)) if settings.get("provider", DEFAULT_PROVIDER) in provider_list else 0
    col1, col2 = st.columns(2)
    with col1: provider = st.selectbox("API 厂商", provider_list, index=provider_idx, key="set_provider")
    with col2:
        models = API_PROVIDERS[provider]["models"]
        model_idx = models.index(settings.get("model", "")) if settings.get("model", "") in models else 0
        model = st.selectbox("模型", models, index=model_idx, key="set_model")

    api_key = st.text_input("API Key", type="password", placeholder="请输入 API Key", value=current_key if current_key else "", key="set_apikey")

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("💾 保存", type="primary", use_container_width=True):
            if not api_key or len(api_key) < 10:
                st.error("❌ 请输入有效的 API Key")
            else:
                save_settings({"api_key": api_key, "provider": provider, "model": model})
                st.session_state.engine = TCMDiagnosisEngine(api_key, provider, model)
                st.session_state.engine_key = f"{provider}:{api_key}"
                st.success(f"✅ 已保存：{provider} / {model}")
                st.rerun()
    with c2:
        if st.button("🧪 测试连接", use_container_width=True):
            if not api_key or len(api_key) < 10:
                st.error("❌ 请先输入 API Key")
            else:
                with st.spinner("测试中..."):
                    try:
                        test_engine = TCMDiagnosisEngine(api_key, provider, model)
                        if not getattr(test_engine, "has_api_key", False):
                            st.error("❌ 客户端初始化失败")
                        else:
                            result = test_engine.analyze_symptoms("测试主诉：头痛", [], "", "")
                            if isinstance(result, dict) and result.get("confidence", 0) > 0:
                                st.success("✅ 连接成功！")
                            else:
                                st.error(f"❌ {result.get('additional_notes', '连接失败')}")
                    except Exception as e:
                        st.error(f"❌ 测试异常：{str(e)[:160]}")
    with c3:
        if st.button("🗑️ 清除配置", use_container_width=True):
            save_settings({"api_key": "", "provider": DEFAULT_PROVIDER, "model": ""})
            st.info("已清除")
            st.rerun()

    if has_api_key := bool(current_key):
        st.success(f"🔑 已配置：{settings.get('provider', DEFAULT_PROVIDER)} / {settings.get('model', '默认模型')}")
    else:
        st.warning("⚠️ 未配置 API Key")

    if supabase_configured():
        st.success("☁️ 数据存储：Supabase 云端")
    else:
        st.warning("💾 数据存储：本地 JSON")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**🗄️ 数据管理**")
    records = load_records()
    st.info(f"📊 共 {len(records)} 条问诊记录")
    if st.button("🗑️ 清空所有记录", use_container_width=True):
        if supabase_configured():
            _sb_clear_records()
        else:
            save_records([])
        st.success("已清空")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
