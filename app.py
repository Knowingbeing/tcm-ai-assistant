import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
from data.ten_asks import ALL_ASKS, TEN_ASKS, DEFAULT_TEN_ASKS, TONGUE_ASK, PULSE_ASK

st.set_page_config(
    page_title="中医AI智能问诊助手",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 强制 UTF-8 编码声明（防止某些浏览器/中间代理把中文当 Latin-1 渲染）
st.markdown(
    '<meta charset="utf-8">'
    '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">',
    unsafe_allow_html=True,
)

st.markdown("""
<style>
    /* ============================================
       清新山水风格 · 中医AI智能问诊助手
       主色：荷绿 #0F7A6A
       辅色：琥珀 #D4A24A / 砚墨 #1F2933
       背景：米白 #FAF8F3
       ============================================ */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap');

    :root {
        --c-primary: #0F7A6A;
        --c-primary-soft: #E6F2EF;
        --c-primary-dark: #0A5A4D;
        --c-amber: #D4A24A;
        --c-amber-soft: #FBF3E3;
        --c-ink: #1F2933;
        --c-ink-soft: #5A6573;
        --c-bg: #FAF8F3;
        --c-bg-card: #FFFFFF;
        --c-line: #EAE5D9;
        --c-success: #4FAE7A;
        --c-warning: #E0A24A;
        --c-danger: #D85A5A;
        --shadow-sm: 0 1px 2px rgba(31, 41, 51, 0.04), 0 1px 3px rgba(31, 41, 51, 0.06);
        --shadow-md: 0 2px 6px rgba(31, 41, 51, 0.05), 0 6px 16px rgba(31, 41, 51, 0.06);
        --shadow-lg: 0 4px 12px rgba(31, 41, 51, 0.06), 0 16px 32px rgba(31, 41, 51, 0.08);
        --radius-sm: 8px;
        --radius-md: 14px;
        --radius-lg: 20px;
        --radius-xl: 28px;
    }

    html, body, .stApp, [data-testid="stAppViewContainer"], [class*="css"] {
        font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }

    /* ===== 全局背景：米白底 + 极淡山水纹理 ===== */
    .stApp {
        background: #FAF8F3;
        background-image:
            radial-gradient(circle at 0% 0%, rgba(15, 122, 106, 0.04) 0%, transparent 50%),
            radial-gradient(circle at 100% 100%, rgba(212, 162, 74, 0.05) 0%, transparent 50%);
    }

    [data-testid="stAppViewContainer"] > .main {
        padding-top: 1rem;
        padding-bottom: 3rem;
    }

    /* 隐藏 streamlit 默认 header/footer/工具栏 */
    [data-testid="stHeader"], [data-testid="stToolbar"], #MainMenu, footer { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    .viewerBadge_link__qRIco { display: none !important; }

    /* ===== 顶部 Hero：横幅式品牌区 ===== */
    .hero-wrap {
        position: relative;
        margin-bottom: 1.6rem;
        padding: 1.6rem 2rem;
        background: linear-gradient(135deg, #FFFFFF 0%, #F2F1E8 100%);
        border: 1px solid var(--c-line);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-sm);
        overflow: hidden;
    }
    .hero-wrap::before {
        content: '';
        position: absolute;
        top: -60px; right: -60px;
        width: 220px; height: 220px;
        background: radial-gradient(circle, rgba(15, 122, 106, 0.12), transparent 70%);
        border-radius: 50%;
    }
    .hero-wrap::after {
        content: '';
        position: absolute;
        bottom: -80px; right: 120px;
        width: 180px; height: 180px;
        background: radial-gradient(circle, rgba(212, 162, 74, 0.10), transparent 70%);
        border-radius: 50%;
    }
    .hero-brand {
        display: flex; align-items: center; gap: 0.9rem;
        position: relative; z-index: 1;
    }
    .hero-logo {
        width: 48px; height: 48px;
        background: linear-gradient(135deg, #0F7A6A, #14A892);
        border-radius: 14px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.6rem; color: white;
        box-shadow: 0 4px 12px rgba(15, 122, 106, 0.25);
    }
    .hero-text h1 {
        margin: 0 !important;
        font-size: 1.65rem !important;
        font-weight: 700 !important;
        color: var(--c-ink) !important;
        letter-spacing: -0.3px;
    }
    .hero-text p {
        margin: 0.2rem 0 0 0;
        font-size: 0.88rem;
        color: var(--c-ink-soft);
    }
    .hero-tags {
        display: flex; flex-wrap: wrap; gap: 0.5rem;
        margin-top: 0.9rem; position: relative; z-index: 1;
    }
    .hero-tag {
        font-size: 0.78rem; padding: 0.25rem 0.7rem;
        background: var(--c-primary-soft); color: var(--c-primary-dark);
        border-radius: 999px; font-weight: 500;
    }
    .hero-tag.amber { background: var(--c-amber-soft); color: #8B6A2E; }

    /* 顶部右侧状态徽章 */
    .hero-status { position: absolute; top: 1.6rem; right: 2rem; display: flex; gap: 0.5rem; z-index: 1; }
    .status-pill {
        font-size: 0.75rem; padding: 0.3rem 0.7rem;
        border-radius: 999px; font-weight: 500;
        background: white; border: 1px solid var(--c-line);
        display: inline-flex; align-items: center; gap: 0.35rem;
        color: var(--c-ink-soft);
    }
    .status-pill .dot { width: 6px; height: 6px; border-radius: 50%; background: var(--c-success); }
    .status-pill.warn .dot { background: var(--c-warning); }

    /* ===== 快速入口卡片 ===== */
    .quick-grid {
        display: grid; grid-template-columns: repeat(4, 1fr);
        gap: 0.9rem; margin-bottom: 1.6rem;
    }
    .quick-card {
        background: white; border: 1px solid var(--c-line);
        border-radius: var(--radius-md); padding: 1.1rem;
        display: flex; align-items: center; gap: 0.9rem;
        transition: all 0.25s ease; cursor: default;
    }
    .quick-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); border-color: var(--c-primary); }
    .quick-icon {
        width: 42px; height: 42px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.3rem; flex-shrink: 0;
    }
    .quick-icon.green { background: var(--c-primary-soft); color: var(--c-primary-dark); }
    .quick-icon.amber { background: var(--c-amber-soft); color: #8B6A2E; }
    .quick-icon.blue { background: #E8EFF7; color: #3A6B9E; }
    .quick-icon.purple { background: #EFE6F2; color: #7A4E8C; }
    .quick-info .label { font-size: 0.78rem; color: var(--c-ink-soft); }
    .quick-info .value { font-size: 1.15rem; font-weight: 600; color: var(--c-ink); }

    /* ===== 通用卡片 / 容器 ===== */
    .card {
        background: var(--c-bg-card);
        border: 1px solid var(--c-line);
        border-radius: var(--radius-md);
        padding: 1.4rem;
        margin-bottom: 1.2rem;
        box-shadow: var(--shadow-sm);
    }
    .card-title {
        display: flex; align-items: center; gap: 0.6rem;
        font-size: 1.02rem; font-weight: 600; color: var(--c-ink);
        margin: 0 0 1rem 0; padding-bottom: 0.8rem;
        border-bottom: 1px solid var(--c-line);
    }
    .card-title .ti {
        width: 28px; height: 28px; border-radius: 8px;
        background: var(--c-primary-soft); color: var(--c-primary-dark);
        display: flex; align-items: center; justify-content: center;
        font-size: 0.95rem;
    }

    /* ===== Tabs 横向导航条（sticky） ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: white;
        padding: 0.4rem;
        border-radius: var(--radius-md);
        border: 1px solid var(--c-line);
        box-shadow: var(--shadow-sm);
        position: sticky; top: 0; z-index: 50;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px; padding: 0 1.1rem;
        border-radius: 10px; font-weight: 500;
        color: var(--c-ink-soft); background: transparent;
        border: none; transition: all 0.2s ease;
        font-size: 0.92rem;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--c-primary);
        background: var(--c-primary-soft);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0F7A6A, #14A892) !important;
        color: white !important;
        box-shadow: 0 2px 8px rgba(15, 122, 106, 0.3);
    }
    div[data-baseweb="tab-panel"] { padding-top: 1.2rem; }

    /* ===== 按钮 ===== */
    .stButton>button {
        background: linear-gradient(135deg, #0F7A6A 0%, #14A892 100%);
        color: white; border: none;
        border-radius: 10px; padding: 0.6rem 1.4rem;
        font-weight: 500; font-size: 0.92rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 6px rgba(15, 122, 106, 0.2);
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(15, 122, 106, 0.3);
    }
    .stButton>button:active { transform: translateY(0); }
    .stButton>button:focus { outline: none; box-shadow: 0 0 0 3px rgba(15, 122, 106, 0.2); }
    .stButton>button:disabled {
        background: #D8D4C7; color: #918A7A; box-shadow: none; transform: none;
    }

    /* 次要按钮（用 key 后缀识别） */
    .stButton>button[kind="secondary"] {
        background: white; color: var(--c-ink);
        border: 1px solid var(--c-line);
        box-shadow: none;
    }
    .stButton>button[kind="secondary"]:hover {
        background: var(--c-primary-soft); color: var(--c-primary-dark);
        border-color: var(--c-primary);
    }

    /* ===== 指标卡 ===== */
    div[data-testid="stMetric"] {
        background: white; padding: 1.1rem;
        border-radius: var(--radius-md);
        border: 1px solid var(--c-line);
        box-shadow: var(--shadow-sm);
    }
    div[data-testid="stMetric"] label {
        color: var(--c-ink-soft) !important;
        font-weight: 500 !important; font-size: 0.82rem !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: var(--c-ink) !important;
        font-weight: 700 !important; font-size: 1.5rem !important;
    }

    /* ===== 输入控件 ===== */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div,
    .stMultiSelect>div>div,
    .stNumberInput>div>div>input {
        border-radius: 10px !important;
        border: 1.5px solid var(--c-line) !important;
        background: white;
        transition: all 0.2s ease;
    }
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus,
    .stNumberInput>div>div>input:focus {
        border-color: var(--c-primary) !important;
        box-shadow: 0 0 0 3px rgba(15, 122, 106, 0.1) !important;
    }
    .stTextInput>label, .stTextArea>label,
    .stSelectbox>label, .stMultiSelect>label,
    .stNumberInput>label { color: var(--c-ink) !important; font-weight: 500 !important; }

    /* ===== 提示类 ===== */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 10px; border-left-width: 3px;
    }
    .stSuccess { background: #ECF7F1; border-left-color: var(--c-success); }
    .stError { background: #FCEAEA; border-left-color: var(--c-danger); }
    .stWarning { background: #FCF3E1; border-left-color: var(--c-amber); }
    .stInfo { background: #EAF1F7; border-left-color: #3A6B9E; }

    /* ===== 展开器 ===== */
    .streamlit-expanderHeader, [data-testid="stExpander"] details summary {
        background: white !important;
        border: 1px solid var(--c-line) !important;
        border-radius: 10px !important;
        font-weight: 500 !important; color: var(--c-ink) !important;
        transition: all 0.2s ease;
    }
    [data-testid="stExpander"] details summary:hover {
        background: var(--c-primary-soft) !important;
        border-color: var(--c-primary) !important;
    }
    [data-testid="stExpander"] details[open] summary {
        background: var(--c-primary-soft) !important;
        border-color: var(--c-primary) !important;
        color: var(--c-primary-dark) !important;
        border-radius: 10px 10px 0 0 !important;
    }
    [data-testid="stExpander"] details > div {
        border: 1px solid var(--c-line) !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
    }

    /* ===== 知识库 grid 卡片 ===== */
    .grid {
        display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 1rem;
    }
    .grid-card {
        background: white; border: 1px solid var(--c-line);
        border-radius: var(--radius-md); padding: 1.1rem;
        transition: all 0.25s ease; cursor: pointer;
        display: flex; flex-direction: column; gap: 0.5rem;
        min-height: 130px;
    }
    .grid-card:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-md);
        border-color: var(--c-primary);
    }
    .grid-card .head {
        display: flex; align-items: center; justify-content: space-between;
        gap: 0.5rem;
    }
    .grid-card .name {
        font-size: 1.02rem; font-weight: 600; color: var(--c-ink);
    }
    .grid-card .chip {
        font-size: 0.72rem; padding: 0.15rem 0.55rem;
        background: var(--c-primary-soft); color: var(--c-primary-dark);
        border-radius: 999px; font-weight: 500;
    }
    .grid-card .chip.amber { background: var(--c-amber-soft); color: #8B6A2E; }
    .grid-card .meta {
        font-size: 0.82rem; color: var(--c-ink-soft);
        display: flex; flex-wrap: wrap; gap: 0.4rem;
    }
    .grid-card .meta span {
        background: #F5F2E9; padding: 0.1rem 0.5rem; border-radius: 6px;
    }
    .grid-card .body { font-size: 0.85rem; color: var(--c-ink-soft); line-height: 1.5; }

    /* ===== 诊断结果堆叠卡片 ===== */
    .result-stack { display: flex; flex-direction: column; gap: 0.9rem; }
    .result-hero {
        background: linear-gradient(135deg, #0F7A6A 0%, #14A892 100%);
        color: white; padding: 1.4rem 1.6rem;
        border-radius: var(--radius-md);
        box-shadow: 0 4px 16px rgba(15, 122, 106, 0.2);
    }
    .result-hero.fail {
        background: linear-gradient(135deg, #C66 0%, #E08383 100%);
    }
    .result-hero .label { font-size: 0.78rem; opacity: 0.85; }
    .result-hero .value { font-size: 1.5rem; font-weight: 700; margin-top: 0.2rem; }
    .result-hero .row { display: flex; gap: 1.6rem; margin-top: 0.9rem; flex-wrap: wrap; }
    .result-hero .col .lab { font-size: 0.72rem; opacity: 0.8; }
    .result-hero .col .val { font-size: 1.05rem; font-weight: 600; margin-top: 0.1rem; }

    .confidence-bar {
        height: 6px; background: rgba(255,255,255,0.25);
        border-radius: 3px; overflow: hidden; margin-top: 0.5rem;
    }
    .confidence-bar .fill {
        height: 100%; background: white; border-radius: 3px;
        transition: width 0.6s ease;
    }

    .result-card {
        background: white; border: 1px solid var(--c-line);
        border-radius: var(--radius-md); padding: 1.1rem 1.3rem;
    }
    .result-card .head {
        display: flex; align-items: center; gap: 0.5rem;
        font-size: 0.88rem; font-weight: 600; color: var(--c-primary-dark);
        margin-bottom: 0.5rem;
    }
    .result-card .body { color: var(--c-ink); line-height: 1.6; font-size: 0.92rem; }
    .result-card .formula {
        font-size: 1.15rem; font-weight: 700; color: var(--c-primary);
        margin-bottom: 0.4rem;
    }

    /* ===== 空态 ===== */
    .empty-state {
        text-align: center; padding: 3rem 1.5rem;
        color: var(--c-ink-soft);
    }
    .empty-state .icon { font-size: 3rem; opacity: 0.4; margin-bottom: 0.5rem; }
    .empty-state .title { font-size: 1.05rem; color: var(--c-ink); margin-bottom: 0.3rem; }
    .empty-state .desc { font-size: 0.88rem; }

    /* ===== 多轮问诊：聊天卡片 ===== */
    .chat-card {
        background: var(--c-surface);
        border-radius: 16px;
        padding: 1.2rem 1.2rem 0.9rem;
        border: 1px solid var(--c-line);
        box-shadow: var(--shadow-sm);
        display: flex;
        flex-direction: column;
        min-height: 540px;
    }
    .chat-card .card-title { display: flex; align-items: center; }
    .chat-card .stChatMessage { background: transparent !important; }

    /* ===== 追问引导块 ===== */
    .followup-block {
        background: linear-gradient(135deg, #FFF9E8 0%, #FFF5D6 100%);
        border-left: 3px solid var(--c-amber);
        border-radius: 10px;
        padding: 0.9rem 1rem;
        margin: 0.6rem 0 0.4rem;
    }
    .q-label {
        font-size: 0.88rem;
        font-weight: 600;
        color: #5C4A1E;
        margin: 0.5rem 0 0.4rem;
    }
    .q-label:first-child { margin-top: 0; }

    /* ===== 分隔条 ===== */
    .divider {
        height: 1px; background: var(--c-line);
        margin: 1.2rem 0;
    }

    /* ===== 数据表格 ===== */
    .stDataFrame, [data-testid="stDataFrame"] {
        border-radius: var(--radius-md);
        overflow: hidden; border: 1px solid var(--c-line);
    }

    /* ===== 移动端 ===== */
    @media (max-width: 768px) {
        .quick-grid { grid-template-columns: repeat(2, 1fr); }
        .hero-status { position: static; margin-top: 0.8rem; }
        .hero-wrap { padding: 1.2rem 1.3rem; }
        .hero-text h1 { font-size: 1.3rem !important; }
    }

    /* ===== 滚动条 ===== */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #D8D4C7; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--c-ink-soft); }
</style>
""", unsafe_allow_html=True)

# 数据目录：始终放在 app.py 同级目录下的 data/，不用 /tmp（Streamlit Cloud 上 /tmp 是临时的）
_APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(_APP_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
RECORDS_FILE = os.path.join(DATA_DIR, "tcm_records.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "tcm_settings.json")


def _row_to_record(row: Dict) -> Dict:
    """将 Supabase 行映射为上层 UI 期望的 record 格式。"""
    return {
        "id": row.get("id"),
        "name": row.get("name", "匿名"),
        "age": row.get("age", 0) or 0,
        "gender": row.get("gender", ""),
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


@st.cache_data(ttl=30)
def load_records():
    """读取问诊记录：优先 Supabase，未配置时回退 JSON 文件。
    缓存 30 秒，保存后调用 load_records.clear() 立即刷新。
    """
    if supabase_configured():
        rows = _sb_get_records()
        result = [_row_to_record(r) for r in rows]
        # 调试日志：首次加载/条数异常时给提示
        if not result:
            print("[load_records] Supabase 已配置但返回 0 条记录，请检查 consultations 表是否为空或表结构是否兼容")
        return result
    if os.path.exists(RECORDS_FILE):
        try:
            with open(RECORDS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []


def save_records(records):
    """保存问诊记录。Supabase 模式下走单条插入；JSON 模式直接覆盖写文件。"""
    if supabase_configured():
        # Supabase 模式下不批量覆盖，由上层逐条调 _sb_save_record
        for r in records:
            ok, _err = _sb_save_record(r)
        return
    with open(RECORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def load_settings():
    """读取系统设置：优先 Supabase，未配置时回退 JSON 文件。"""
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
    """保存系统设置。Supabase 模式 upsert 到单行；JSON 模式保持原行为。"""
    if supabase_configured():
        _sb_save_settings(settings)
        return
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

def get_engine():
    """返回 AI 引擎单例；同时在 session_state 里维护 _api_key_ok 标志位供 UI 同步读取。"""
    settings = load_settings()
    api_key = settings.get("api_key", DEFAULT_API_KEY)
    provider = settings.get("provider", DEFAULT_PROVIDER)
    model = settings.get("model", "")

    engine_key = f"{provider}:{api_key}"
    if "engine" not in st.session_state or st.session_state.get("engine_key") != engine_key:
        st.session_state.engine = TCMDiagnosisEngine(api_key, provider, model)
        st.session_state.engine_key = engine_key
        # 把 key 是否"形式上有效"写进标志位（不依赖网络探测，保证 UI 同步）
        st.session_state._api_key_ok = bool(api_key and len(api_key) >= 10)
    return st.session_state.engine

def main():
    # 多轮问诊 — 会话状态初始化
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = {}
    if "_api_key_ok" not in st.session_state:
        st.session_state._api_key_ok = False
    engine = get_engine()
    # ★ 四路判定（覆盖所有场景：已保存 / engine 对象 / 磁盘持久化 / widget 持久化）
    _disk_key = (load_settings().get("api_key") or "").strip()
    _widget_val = str(st.session_state.get("cfg_api_key", "") or "").strip()
    has_api_key = (
        bool(st.session_state.get("_api_key_ok", False))     # ① 保存按钮写入的标志位
        or bool(getattr(engine, "has_api_key", False))       # ② engine 初始化成功
        or bool(_disk_key and len(_disk_key) >= 10)          # ③ 磁盘/云端 settings
        or bool(_widget_val and len(_widget_val) >= 10)      # ④ 输入框 widget 值（Streamlit 跨 rerun 持久）
    )
    settings = load_settings()
    records = load_records()
    sb_ok = supabase_configured()
    today = datetime.now().strftime("%Y-%m-%d")

    # 模型名：优先读 session_state（保存后立即生效），其次读 settings
    _cfg = settings
    model_name = _cfg.get("model", "") or API_PROVIDERS.get(_cfg.get("provider", DEFAULT_PROVIDER), {}).get("default_model", "")
    if has_api_key:
        model_name = st.session_state.get("engine", engine).model if hasattr(engine, "model") else model_name

    # 状态徽章
    if has_api_key and sb_ok:
        status_pill = '<span class="status-pill"><span class="dot"></span>系统就绪</span>'
    elif not has_api_key:
        status_pill = '<span class="status-pill warn"><span class="dot"></span>未配置 API Key</span>'
    elif not sb_ok:
        status_pill = '<span class="status-pill warn"><span class="dot"></span>本地存储</span>'
    else:
        status_pill = '<span class="status-pill"><span class="dot"></span>运行中</span>'

    today_pill = f'<span class="status-pill">{today}</span>'

    st.markdown(f"""
    <div class="hero-wrap">
        <div class="hero-status">{status_pill}{today_pill}</div>
        <div class="hero-brand">
            <div class="hero-logo">🩺</div>
            <div class="hero-text">
                <h1>中医 AI 智能问诊助手</h1>
                <p>传承千年岐黄之术，融合现代大语言模型，让辨证论治更轻、更准、更贴心</p>
            </div>
        </div>
        <div class="hero-tags">
            <span class="hero-tag">六经辨证</span>
            <span class="hero-tag">脏腑辨证</span>
            <span class="hero-tag">卫气营血</span>
            <span class="hero-tag amber">87 味常用中药</span>
            <span class="hero-tag amber">中医经典方剂</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 快速入口
    avg_conf = 0
    valid = [r for r in records if r.get("confidence", 0) > 0]
    if valid:
        avg_conf = sum(r.get("confidence", 0) for r in valid) / len(valid)

    st.markdown(f"""
    <div class="quick-grid">
        <div class="quick-card">
            <div class="quick-icon green">📋</div>
            <div class="quick-info">
                <div class="label">总问诊数</div>
                <div class="value">{len(records)}</div>
            </div>
        </div>
        <div class="quick-card">
            <div class="quick-icon amber">🎯</div>
            <div class="quick-info">
                <div class="label">平均置信度</div>
                <div class="value">{avg_conf:.0f}%</div>
            </div>
        </div>
        <div class="quick-card">
            <div class="quick-icon blue">💾</div>
            <div class="quick-info">
                <div class="label">数据存储</div>
                <div class="value" style="font-size:0.95rem">{'☁️ Supabase' if sb_ok else '💾 本地 JSON'}</div>
            </div>
        </div>
        <div class="quick-card">
            <div class="quick-icon purple">🤖</div>
            <div class="quick-info">
                <div class="label">AI 模型</div>
                <div class="value" style="font-size:0.95rem">{model_name[:14]}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋  智能问诊", "📊  数据分析", "📚  知识库", "🌿  中药库", "⚙️  系统设置"])

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
    """多轮问诊 tab
    模式：左 sticky 表单（基础信息+主诉） + 右 chat 窗口（AI 主动追问 → 引导选择 → 最终辨证）
    状态：st.session_state.chat_session = {
        "session_id": str (uuid),
        "round": int,
        "messages": [{role, content, ts, kind}],
        "pending_questions": [...],
        "chief_complaint": str,
        "symptoms": [],
        "tongue_sign": "",
        "pulse_sign": "",
        "patient": {name, age, gender},
        "result": {...} | None,
    }
    """
    import uuid as _uuid
    from datetime import datetime as _dt

    # 初始化会话
    sess = st.session_state.chat_session
    if not sess.get("session_id"):
        sess["session_id"] = str(_uuid.uuid4())
        sess["round"] = 0
        sess["messages"] = []
        sess["pending_questions"] = []
        sess["chief_complaint"] = ""
        sess["symptoms"] = []
        sess["tongue_sign"] = ""
        sess["pulse_sign"] = ""
        sess["patient"] = {"name": "匿名", "age": 30, "gender": "男"}
        sess["result"] = None
        # 欢迎语
        sess["messages"].append({
            "role": "assistant",
            "kind": "greeting",
            "content": "你好，我是你的中医 AI 助手 🩺\n请告诉我你哪里不舒服？我会通过 1-2 个关键问题帮你辨证。",
            "ts": _dt.now().strftime("%H:%M:%S"),
        })

    # ===== 顶部卡片 =====
    st.markdown("""
    <div class="card">
        <div class="card-title"><div class="ti">📋</div>多轮智能问诊</div>
        <p style="color:var(--c-ink-soft); margin:0; font-size:0.9rem;">
            AI 将根据你提供的信息主动追问 1-2 个关键问题。问完后再做辨证。
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.6], gap="large")

    # ===================== 左侧：基础信息 + 主诉 =====================
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("""
        <div class="card-title"><div class="ti">👤</div>患者信息</div>
        """, unsafe_allow_html=True)
        sess["patient"]["name"] = st.text_input(
            "姓名", value=sess["patient"].get("name", "匿名"),
            placeholder="可填可不填", label_visibility="collapsed",
            key="chat_patient_name",
        )
        c1, c2 = st.columns(2)
        with c1:
            sess["patient"]["age"] = st.number_input(
                "年龄", min_value=0, max_value=150,
                value=int(sess["patient"].get("age", 30)),
                key="chat_patient_age",
            )
        with c2:
            gender_idx = 0 if sess["patient"].get("gender", "男") == "男" else 1
            sess["patient"]["gender"] = st.selectbox(
                "性别", ["男", "女"], index=gender_idx, key="chat_patient_gender",
            )

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="card-title"><div class="ti">📝</div>主诉与症状</div>
        """, unsafe_allow_html=True)
        chief = st.text_area(
            "主诉",
            value=sess.get("chief_complaint", ""),
            placeholder="例如：最近 3 天头痛、怕冷、不出汗",
            height=100, label_visibility="collapsed",
            key="chat_chief",
        )
        sess["chief_complaint"] = chief

        # ===== 十问歌结构化问诊 =====
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="card-title"><div class="ti">📋</div>十问歌（结构化问诊）</div>
        <p style="color:var(--c-ink-soft); margin:0; font-size:0.85rem;">
            按中医十问歌逐项填写，帮助AI更准确辨证
        </p>
        """, unsafe_allow_html=True)

        # 初始化十问歌数据
        if "ten_asks_data" not in sess:
            sess["ten_asks_data"] = dict(DEFAULT_TEN_ASKS)

        # 分阶段显示十问歌
        for stage in [1, 2, 3]:
            stage_asks = [ask for ask in TEN_ASKS if ask.get("stage") == stage]
            if stage_asks:
                with st.expander(f"第{stage}阶段问诊", expanded=(stage == 1)):
                    for ask in stage_asks:
                        key = ask["key"]
                        label = f"{ask['icon']} {ask['label']}"

                        if ask.get("input_type") == "text":
                            # 文本输入型（如旧病、舌诊）
                            value = st.text_input(
                                label,
                                value=sess["ten_asks_data"].get(key, ""),
                                placeholder=ask.get("placeholder", ""),
                                key=f"ten_{key}",
                            )
                            sess["ten_asks_data"][key] = value
                        elif ask.get("multi"):
                            # 多选型（如头身、胸腹）
                            current = sess["ten_asks_data"].get(key, {})
                            if isinstance(current, dict):
                                current = current.get("parts", [])
                            selected = st.multiselect(
                                label,
                                ask["options"],
                                default=[s for s in current if s in ask["options"]],
                                key=f"ten_{key}",
                            )
                            sess["ten_asks_data"][key] = {"parts": selected, "detail": ""}
                        elif "sub_asks" in ask:
                            # 子问题型（如二便、饮食口味）
                            sub_data = sess["ten_asks_data"].get(key, {})
                            if not isinstance(sub_data, dict):
                                sub_data = {}
                            cols = st.columns(len(ask["sub_asks"]))
                            for i, sub in enumerate(ask["sub_asks"]):
                                with cols[i]:
                                    sub_val = st.selectbox(
                                        f"{label}-{sub['label']}",
                                        sub["options"],
                                        index=sub["options"].index(sub_data.get(sub["key"], sub["options"][0])) if sub_data.get(sub["key"]) in sub["options"] else 0,
                                        key=f"ten_{key}_{sub['key']}",
                                    )
                                    sub_data[sub["key"]] = sub_val
                            sess["ten_asks_data"][key] = sub_data
                        else:
                            # 单选型（如寒热、汗）
                            options = ["请选择"] + ask["options"]
                            current_val = sess["ten_asks_data"].get(key, {})
                            if isinstance(current_val, dict):
                                current_val = current_val.get("type", "")
                            current_idx = 0
                            if current_val in options:
                                current_idx = options.index(current_val)
                            selected = st.selectbox(
                                label,
                                options,
                                index=current_idx,
                                key=f"ten_{key}",
                            )
                            sess["ten_asks_data"][key] = {"type": selected if selected != "请选择" else "", "detail": ""}

        # 女性经期问诊（仅女性显示）
        if sess["patient"].get("gender") == "女":
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            with st.expander("🌸 经期问诊（女性）", expanded=False):
                menstruation = sess["ten_asks_data"].get("menstruation") or {}
                cols = st.columns(4)
                for i, sub in enumerate(MENSTRUATION_ASK["sub_asks"]):
                    with cols[i]:
                        val = st.selectbox(
                            f"月经{sub['label']}",
                            sub["options"],
                            index=sub["options"].index(menstruation.get(sub["key"], sub["options"][0])) if menstruation.get(sub["key"]) in sub["options"] else 0,
                            key=f"ten_menstruation_{sub['key']}",
                        )
                        menstruation[sub["key"]] = val
                sess["ten_asks_data"]["menstruation"] = menstruation

        # 舌诊和脉诊
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            sess["tongue_sign"] = st.text_input(
                "👅 舌象", value=sess.get("tongue_sign", ""),
                placeholder=TONGUE_ASK.get("placeholder", "如：舌淡苔白"),
                label_visibility="collapsed",
                key="chat_tongue",
            )
        with c2:
            pulse_options = ["请选择"] + PULSE_ASK["options"]
            current_pulse = sess.get("pulse_sign", "")
            pulse_idx = 0
            if current_pulse in pulse_options:
                pulse_idx = pulse_options.index(current_pulse)
            selected_pulse = st.selectbox(
                "🫀 脉象",
                pulse_options,
                index=pulse_idx,
                key="chat_pulse",
            )
            sess["pulse_sign"] = selected_pulse if selected_pulse != "请选择" else ""

        # 合并十问歌数据到症状列表
        ten_symptoms = []
        for key, val in sess["ten_asks_data"].items():
            if isinstance(val, dict):
                if "parts" in val:
                    ten_symptoms.extend(val.get("parts", []))
                elif "type" in val and val["type"]:
                    ten_symptoms.append(val["type"])
                elif "stool" in val and val.get("stool"):
                    ten_symptoms.append(f"大便{val['stool']}")
                elif "urine" in val and val.get("urine"):
                    ten_symptoms.append(f"小便{val['urine']}")
                elif "appetite" in val and val.get("appetite"):
                    ten_symptoms.append(val["appetite"])
                elif "thirst" in val and val.get("thirst"):
                    ten_symptoms.append(val["thirst"])
                elif "quality" in val and val.get("quality"):
                    ten_symptoms.append(val["quality"])
            elif isinstance(val, str) and val:
                ten_symptoms.append(val)

        # 合并到症状列表（去重）
        current_symptoms = sess.get("symptoms", [])
        all_symptoms = list(set(current_symptoms + [s for s in ten_symptoms if s and s != "无不适"]))

        all_symptoms_options = [
            "发热", "恶寒", "畏寒", "头痛", "头晕", "咳嗽", "鼻塞", "流涕",
            "咽喉痛", "胸闷", "心悸", "腹痛", "腹泻", "便秘", "食欲不振",
            "口渴", "口苦", "失眠", "乏力", "自汗", "盗汗", "腰膝酸软",
            "畏寒肢冷", "呕吐", "腹胀", "胸胁胀痛", "善太息", "情志抑郁",
            "面红目赤", "急躁易怒", "眩晕", "耳鸣", "多梦", "健忘",
            "气短", "神疲", "四肢厥冷", "干咳少痰", "痰多", "痰黄稠",
            "关节疼痛", "身热不扬", "心烦", "消渴", "刺痛", "面色晦暗",
        ]
        # 确保 default 值是字符串列表且在 all_symptoms 中
        current_symptoms = sess.get("symptoms", [])
        default_symptoms = [s for s in current_symptoms if isinstance(s, str) and s in all_symptoms]
        sess["symptoms"] = st.multiselect(
            "伴随症状", all_symptoms,
            default=default_symptoms,
            label_visibility="collapsed",
            key="chat_symptoms",
        )

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="card-title"><div class="ti">👅</div>舌脉（可选）</div>
        """, unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            sess["tongue_sign"] = st.text_input(
                "舌象", value=sess.get("tongue_sign", ""),
                placeholder="如：舌淡苔白", label_visibility="collapsed",
                key="chat_tongue",
            )
        with c2:
            sess["pulse_sign"] = st.text_input(
                "脉象", value=sess.get("pulse_sign", ""),
                placeholder="如：脉浮紧", label_visibility="collapsed",
                key="chat_pulse",
            )

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            start_clicked = st.button(
                "🚀 开始问诊", type="primary",
                use_container_width=True, key="chat_start",
            )
        with btn_col2:
            reset_clicked = st.button(
                "🔄 重新开始", use_container_width=True, key="chat_reset",
            )

        st.markdown('</div>', unsafe_allow_html=True)

    # ===================== 右侧：聊天窗口 =====================
    with col2:
        st.markdown('<div class="chat-card">', unsafe_allow_html=True)
        st.markdown("""
        <div class="card-title"><div class="ti">💬</div>对话窗口
            <span style="font-size:0.75rem; color:var(--c-ink-soft); font-weight:normal; margin-left:auto;">
                第 <b style="color:var(--c-primary)">{round}</b> 轮
            </span>
        </div>
        """.replace("{round}", str(sess["round"])), unsafe_allow_html=True)

        # 渲染历史消息
        _render_chat_history(sess["messages"])

        # 追问问题：快捷选项
        if sess.get("pending_questions"):
            st.markdown('<div class="followup-block">', unsafe_allow_html=True)
            st.markdown("**🤔 AI 想了解：**", unsafe_allow_html=True)
            for q in sess["pending_questions"]:
                st.markdown(f"<div class='q-label'>{q['label']}</div>", unsafe_allow_html=True)
                cols = st.columns(min(len(q["options"]), 4))
                for idx, opt in enumerate(q["options"]):
                    with cols[idx % 4]:
                        if st.button(
                            opt, key=f"opt_{q['field']}_{idx}",
                            use_container_width=True,
                        ):
                            _apply_followup_answer(sess, q, opt, engine)
                            st.rerun()
            # 自由输入框
            custom = st.text_input(
                "或者用自己的话回答", key="custom_answer",
                placeholder="例如：舌尖红、苔薄黄",
                label_visibility="collapsed",
            )
            if st.button("✉️ 提交回答", use_container_width=True, key="custom_submit"):
                if custom.strip():
                    # 取第一个待追问问题，把 custom 写到对应 field
                    q = sess["pending_questions"][0]
                    _apply_followup_answer(sess, q, custom.strip(), engine)
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # 自由对话输入（仅当无 pending_questions 且无 result）
        elif sess["result"] is None:
            user_msg = st.text_input(
                "继续对话", key="chat_user_msg",
                placeholder="补充症状或问 AI 问题…",
                label_visibility="collapsed",
            )
            c1, c2 = st.columns([3, 1])
            with c1:
                if st.button("📤 发送", type="primary", use_container_width=True, key="chat_send"):
                    if user_msg.strip():
                        sess["messages"].append({
                            "role": "user",
                            "kind": "message",
                            "content": user_msg.strip(),
                            "ts": _dt.now().strftime("%H:%M:%S"),
                        })
                        _maybe_diagnose(sess, engine)
                        st.rerun()
            with c2:
                if st.button("🩺 立即辨证", use_container_width=True, key="chat_force_diag"):
                    _finalize_diagnosis(sess, engine)
                    st.rerun()

        # 已出结果：显示诊断卡 + 保存按钮
        if sess.get("result"):
            _render_result_card(sess)
            csave, cclear = st.columns(2)
            with csave:
                if sess.get("saved"):
                    st.success("✅ 本次问诊已保存")
                    if st.button("🔄 再次保存", use_container_width=True, key="chat_save_again"):
                        sess["saved"] = False
                        st.rerun()
                else:
                    if st.button("💾 保存此次问诊", type="primary",
                                 use_container_width=True, key="chat_save"):
                        _save_chat_session(sess)
                        st.rerun()
            with cclear:
                if st.button("🔄 重新开始", use_container_width=True, key="chat_restart"):
                    _reset_chat_session()
                    st.rerun()
        elif sess.get("messages") and len(sess["messages"]) > 1:
            # 即使没结果，只要发起了对话就允许"保存草稿"
            st.info("💡 当前尚未生成辨证结果，可继续追问，或先保存草稿")
            if st.button("💾 保存对话草稿", use_container_width=True, key="chat_save_draft"):
                _save_draft_session(sess)
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # ===== 按钮事件 =====
    if start_clicked:
        if not sess["chief_complaint"].strip():
            st.toast("⚠️ 请先填写主诉", icon="⚠️")
        else:
            # 用户主动发起：把主诉+症状作为一条 user 消息
            summary = sess["chief_complaint"]
            if sess["symptoms"]:
                summary += "\n伴随症状：" + "、".join(sess["symptoms"])
            sess["messages"].append({
                "role": "user",
                "kind": "complaint",
                "content": summary,
                "ts": _dt.now().strftime("%H:%M:%S"),
            })
            sess["round"] += 1
            _maybe_diagnose(sess, engine)
            st.rerun()

    if reset_clicked:
        _reset_chat_session()
        st.rerun()


# ---------------------------------------------------------------------------
# 多轮问诊 — 内部辅助函数
# ---------------------------------------------------------------------------
def _render_chat_history(messages):
    """渲染聊天历史（按时间倒序: 新消息在底部）"""
    # 简单实现：用 st.chat_message
    for msg in messages:
        role = msg.get("role", "user")
        kind = msg.get("kind", "message")
        content = msg.get("content", "")
        ts = msg.get("ts", "")
        with st.chat_message(name="user" if role == "user" else "assistant"):
            if kind == "greeting":
                st.markdown(f"**中医 AI 助手** · _{ts}_  \n\n{content}")
            elif kind == "complaint":
                st.markdown(f"**你** · _{ts}_  \n\n{content}")
            elif kind == "followup_answer":
                st.markdown(f"**你** · _{ts}_  \n\n{content}")
            elif kind == "diagnosis":
                # 诊断结论用卡片渲染（在 chat 内部）
                _render_result_inline(content, ts)
            else:
                st.markdown(f"**{'你' if role == 'user' else 'AI'}** · _{ts}_  \n\n{content}")


def _render_result_inline(result: Dict, ts: str):
    """在 chat 内部紧凑地渲染诊断结果"""
    is_ok = result.get("confidence", 0) > 0
    cls = "" if is_ok else " fail"
    conf = result.get("confidence", 0)
    st.markdown(f"""
    <div class="result-stack" style="margin-top:0.4rem">
        <div class="result-hero{cls}" style="padding:0.9rem 1rem">
            <div class="label">{'✅ 辨证完成' if is_ok else '❌ 辨证失败'} · {ts}</div>
            <div class="value" style="font-size:1.3rem">🩺 {result.get('syndrome','')}</div>
            <div class="row">
                <div class="col">
                    <div class="lab">辨证体系</div>
                    <div class="val">{result.get('syndrome_category', '待分类')}</div>
                </div>
                <div class="col">
                    <div class="lab">置信度</div>
                    <div class="val">{conf}%</div>
                    <div class="confidence-bar"><div class="fill" style="width:{min(conf,100)}%"></div></div>
                </div>
            </div>
        </div>
        <div class="result-card">
            <div class="head">📖 辨证分析</div>
            <div class="body">{result.get('analysis','')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if result.get("treatment_principle") and result["treatment_principle"] not in ("无", ""):
        st.markdown(f"""
        <div class="result-card">
            <div class="head">🎯 治疗原则</div>
            <div class="body">{result['treatment_principle']}</div>
        </div>
        """, unsafe_allow_html=True)
    formula = result.get("formula", "")
    if formula and formula not in ("无", "待推荐"):
        st.markdown(f"""
        <div class="result-card">
            <div class="head">💊 推荐方剂</div>
            <div class="formula">{formula}</div>
        </div>
        """, unsafe_allow_html=True)
    if result.get("formula_adjustment") and result["formula_adjustment"] not in ("无", ""):
        st.markdown(f"""
        <div class="result-card" style="border-left:3px solid var(--c-amber)">
            <div class="head" style="color:#8B6A2E">🧩 加减建议</div>
            <div class="body">{result['formula_adjustment']}</div>
        </div>
        """, unsafe_allow_html=True)
    if result.get("additional_notes") and result["additional_notes"] not in ("无", ""):
        st.markdown(f"""
        <div class="result-card" style="border-left:3px solid var(--c-warning)">
            <div class="head" style="color:#A8782E">💡 提示</div>
            <div class="body">{result['additional_notes']}</div>
        </div>
        """, unsafe_allow_html=True)


def _render_result_card(sess):
    """聊天窗外的最终结果卡（紧凑模式）"""
    result = sess["result"]
    is_ok = result.get("confidence", 0) > 0
    cls = "" if is_ok else " fail"
    conf = result.get("confidence", 0)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="result-stack">
        <div class="result-hero{cls}">
            <div class="label">{'✅ 最终辨证' if is_ok else '❌ 辨证失败'}</div>
            <div class="value">🩺 {result.get('syndrome','')}</div>
            <div class="row">
                <div class="col">
                    <div class="lab">辨证体系</div>
                    <div class="val">{result.get('syndrome_category','待分类')}</div>
                </div>
                <div class="col">
                    <div class="lab">置信度</div>
                    <div class="val">{conf}%</div>
                    <div class="confidence-bar"><div class="fill" style="width:{min(conf,100)}%"></div></div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _maybe_diagnose(sess, engine):
    """判断是否可以直接辨证，否则生成追问。"""
    # 防御：engine 不可用时直接走规则辨证
    if engine is None or not hasattr(engine, "should_ask_followup"):
        _finalize_diagnosis(sess, engine)
        return
    # 修正：round_count 是"已追问过的轮数"，用 sess["round"] 才是对的
    # （旧的 len(pending_questions) 语义错乱，会让第二轮立刻强制收尾）
    try:
        followup = engine.should_ask_followup(
            sess["chief_complaint"], sess["symptoms"],
            sess["tongue_sign"], sess["pulse_sign"],
            round_count=sess.get("round", 0),
        )
    except Exception as e:
        # 追问判断失败 → 直接收尾
        from datetime import datetime as _dt
        sess["messages"].append({
            "role": "assistant",
            "kind": "message",
            "content": f"⚠️ 追问判断异常：{str(e)[:120]}，将直接进行辨证。",
            "ts": _dt.now().strftime("%H:%M:%S"),
        })
        _finalize_diagnosis(sess, engine)
        return
    from datetime import datetime as _dt
    if not followup or not isinstance(followup, dict):
        _finalize_diagnosis(sess, engine)
        return
    if followup.get("need_followup"):
        sess["pending_questions"] = followup.get("questions", []) or []
        msg_lines = [f"为了更准确地辨证，我需要再了解几项信息："]
        for q in sess["pending_questions"]:
            label = q.get("label", str(q))
            msg_lines.append(f"• {label}")
        sess["messages"].append({
            "role": "assistant",
            "kind": "followup",
            "content": "\n".join(msg_lines),
            "ts": _dt.now().strftime("%H:%M:%S"),
        })
    else:
        _finalize_diagnosis(sess, engine)


def _apply_followup_answer(sess, q, opt, engine):
    """处理追问回答：把答案写回对应字段，清除该追问，再判断是否还要继续"""
    from datetime import datetime as _dt
    field = q["field"]
    # 写回 session 字段
    if field in ("tongue_sign", "pulse_sign"):
        sess[field] = opt
    elif field == "cold_hot":
        if "畏寒" in opt or "寒" in opt:
            if "畏寒" not in sess["symptoms"]:
                sess["symptoms"].append("畏寒肢冷")
        elif "热" in opt and "畏寒" in opt:
            pass  # 往来寒热
        elif "热" in opt:
            if "畏热" not in sess["symptoms"]:
                sess["symptoms"].append("畏热")
    elif field == "sweat":
        if "无汗" in opt and "无汗" not in sess["symptoms"]:
            sess["symptoms"].append("无汗")
        elif "自汗" in opt and "自汗" not in sess["symptoms"]:
            sess["symptoms"].append("自汗")
        elif "盗汗" in opt and "盗汗" not in sess["symptoms"]:
            sess["symptoms"].append("盗汗")
    elif field == "stool_urine":
        if "稀溏" in opt and "腹泻" not in sess["symptoms"]:
            sess["symptoms"].append("腹泻")
        elif "干结" in opt and "便秘" not in sess["symptoms"]:
            sess["symptoms"].append("便秘")
        elif "短赤" in opt and "小便短赤" not in sess["symptoms"]:
            sess["symptoms"].append("小便短赤")
    # 记录用户回答
    sess["messages"].append({
        "role": "user",
        "kind": "followup_answer",
        "content": f"**{q['label']}** → {opt}",
        "ts": _dt.now().strftime("%H:%M:%S"),
    })
    # 移除该 field
    sess["pending_questions"] = [x for x in sess["pending_questions"] if x["field"] != field]
    # 继续判断
    if sess["pending_questions"]:
        sess["round"] += 1
        # 还有追问，等用户继续
    else:
        sess["round"] += 1
        _finalize_diagnosis(sess, engine)


def _finalize_diagnosis(sess, engine):
    """输出最终辨证结果"""
    from datetime import datetime as _dt
    # 防御：engine 不可用 → 走一个最小的兜底结果
    if engine is None or not hasattr(engine, "analyze_symptoms"):
        result = {
            "syndrome": "诊断暂不可用",
            "syndrome_category": "系统错误",
            "analysis": "AI 引擎未就绪，请前往「系统设置」配置 API Key。",
            "formula": "—", "formula_adjustment": "—",
            "treatment_principle": "—", "confidence": 0,
            "additional_notes": "💡 请先在系统设置中配置 API Key，再开始辨证。",
        }
    else:
        try:
            result = engine.analyze_symptoms(
                sess["chief_complaint"], sess["symptoms"],
                sess["tongue_sign"], sess["pulse_sign"],
            )
            if not isinstance(result, dict):
                result = {"syndrome": "诊断失败", "syndrome_category": "未知",
                          "analysis": str(result)[:200], "formula": "—",
                          "formula_adjustment": "—", "treatment_principle": "—",
                          "confidence": 0, "additional_notes": "请重试或检查 API 配置。"}
        except Exception as e:
            result = {"syndrome": "诊断异常", "syndrome_category": "未知错误",
                      "analysis": f"辨证过程异常：{str(e)[:200]}", "formula": "—",
                      "formula_adjustment": "—", "treatment_principle": "—",
                      "confidence": 0, "additional_notes": "请稍后重试或截图联系开发者。"}
    sess["result"] = result
    is_ok = result.get("confidence", 0) > 0
    text = "✅ 辨证完成" if is_ok else "❌ 辨证失败"
    sess["messages"].append({
        "role": "assistant",
        "kind": "diagnosis",
        "content": result,
        "ts": _dt.now().strftime("%H:%M:%S"),
    })
    # 额外附加一条简短结论
    short = f"**{text}**\n\n**证型**：{result.get('syndrome','')}\n**方剂**：{result.get('formula','')}（置信度 {result.get('confidence',0)}%）"
    sess["messages"].append({
        "role": "assistant",
        "kind": "message",
        "content": short,
        "ts": _dt.now().strftime("%H:%M:%S"),
    })


def _save_chat_session(sess):
    """把当前会话的最终结果写入 Supabase（带 session_id）"""
    result = sess.get("result")
    if not result:
        st.toast("⚠️ 暂无结果可保存", icon="⚠️")
        return
    record = {
        "session_id": sess["session_id"],
        "round_index": sess["round"],
        "name": sess["patient"].get("name", "匿名") or "匿名",
        "age": int(sess["patient"].get("age", 0) or 0),
        "gender": sess["patient"].get("gender", ""),
        "chief_complaint": sess["chief_complaint"],
        "symptoms": sess["symptoms"],
        "tongue_sign": sess["tongue_sign"],
        "pulse_sign": sess["pulse_sign"],
        "syndrome": result.get("syndrome", ""),
        "syndrome_category": result.get("syndrome_category", ""),
        "formula": result.get("formula", ""),
        "formula_adjustment": result.get("formula_adjustment", ""),
        "treatment_principle": result.get("treatment_principle", ""),
        "analysis": result.get("analysis", ""),
        "confidence": int(result.get("confidence", 0) or 0),
        "source": "chat",
        "messages": sess.get("messages", []),
    }
    saved = False
    if supabase_configured():
        ok, err = _sb_save_record(record)
        if ok:
            st.success("✅ 已保存到云端（含完整对话）")
            saved = True
        else:
            st.error(f"❌ 云端保存失败：{err}")
            with st.expander("📋 排查建议", expanded=True):
                st.markdown(f"""
                **错误详情**：`{err}`

                **常见原因**：
                1. **表未创建** → 在 Supabase SQL Editor 执行 `supabase/schema.sql`
                2. **缺字段** → 执行 `supabase/migration_p1_session.sql`（添加 session_id/round_index/messages）
                3. **RLS 拦截** → 执行 `ALTER TABLE consultations DISABLE ROW LEVEL SECURITY;`
                4. **CHECK 约束** → confidence 超出 0-100、gender 不在允许范围、source 不在允许范围
                5. **Key 无效** → 检查 `.streamlit/secrets.toml` 中的 SUPABASE_URL / SUPABASE_KEY
                """)
    else:
        # 本地降级：直接写文件
        from datetime import datetime as _dt
        records = load_records()
        record["id"] = len(records) + 1
        record["date"] = _dt.now().strftime("%Y-%m-%d %H:%M:%S")
        records.append(record)
        try:
            save_records(records)
            st.success(f"✅ 已保存到本地（当前共 {len(records)} 条）")
            saved = True
        except Exception as e:
            st.error(f"❌ 本地保存失败：{str(e)[:120]}")
    if saved:
        sess["saved"] = True
        # 清除 load_records 的缓存，确保数据分析 Tab 立刻读到新数据
        load_records.clear()


def _save_draft_session(sess):
    """保存未完成对话的草稿（含对话历史但无诊断结果）"""
    record = {
        "session_id": sess.get("session_id", ""),
        "round_index": sess.get("round", 0),
        "name": sess.get("patient", {}).get("name", "匿名") or "匿名",
        "age": int(sess.get("patient", {}).get("age", 0) or 0),
        "gender": sess.get("patient", {}).get("gender", ""),
        "chief_complaint": sess.get("chief_complaint", ""),
        "symptoms": sess.get("symptoms", []),
        "tongue_sign": sess.get("tongue_sign", ""),
        "pulse_sign": sess.get("pulse_sign", ""),
        "syndrome": "(未完成)",
        "syndrome_category": "(草稿)",
        "formula": "—", "formula_adjustment": "—",
        "treatment_principle": "—", "analysis": "对话进行中，未生成辨证",
        "confidence": 0,
        "source": "draft",
        "messages": sess.get("messages", []),
    }
    if supabase_configured():
        ok, err = _sb_save_record(record)
        if ok:
            st.success("✅ 草稿已保存到云端")
        else:
            st.error(f"❌ 云端保存失败：{err}")
    else:
        from datetime import datetime as _dt
        records = load_records()
        record["id"] = len(records) + 1
        record["date"] = _dt.now().strftime("%Y-%m-%d %H:%M:%S")
        records.append(record)
        try:
            save_records(records)
            st.success(f"✅ 草稿已保存到本地（共 {len(records)} 条）")
        except Exception as e:
            st.error(f"❌ 保存失败：{str(e)[:120]}")


def _reset_chat_session():
    """重置聊天会话"""
    st.session_state.chat_session = {}


def _sb_save_record(record: Dict) -> tuple:
    """薄包装：调用 utils.supabase_client.save_record（缺列兼容）。
    返回 (success: bool, error_msg: str)。
    """
    from utils.supabase_client import save_record
    return save_record(record)

def render_analytics_tab():
    # 顶部卡片 + 刷新按钮
    ctitle, cbtn = st.columns([6, 1])
    with ctitle:
        st.markdown("""
        <div class="card">
            <div class="card-title"><div class="ti">📊</div>数据分析看板</div>
            <p style="color:var(--c-ink-soft); margin:0; font-size:0.9rem;">
                历次问诊的可视化汇总，帮助你发现常见证型分布与系统表现。
            </p>
        </div>
        """, unsafe_allow_html=True)
    with cbtn:
        st.markdown('<div style="height:1.6rem"></div>', unsafe_allow_html=True)
        if st.button("🔄 刷新", use_container_width=True, key="analytics_refresh"):
            load_records.clear()
            st.rerun()

    # ★ 诊断信息：让用户知道数据从哪来、加载了几条
    backend = "☁️ Supabase" if supabase_configured() else "💾 本地 JSON"
    records = load_records()
    st.markdown(
        f'<div style="color:var(--c-ink-soft); font-size:0.82rem; margin:0.4rem 0 0.8rem 0;">'
        f'📦 存储后端：<b>{backend}</b>　·　已加载 <b>{len(records)}</b> 条记录'
        f'</div>',
        unsafe_allow_html=True,
    )
    valid = [r for r in records if r.get("confidence", 0) > 0]
    avg_conf = sum(r.get("confidence", 0) for r in valid) / len(valid) if valid else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("📋 总问诊数", len(records))
    with col2: st.metric("✅ 有效诊断", len(valid))
    with col3: st.metric("📊 平均置信度", f"{avg_conf:.1f}%")
    with col4:
        last_date = records[-1].get("date", "")[:10] if records else "无"
        st.metric("🕐 最新记录", last_date)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    if not records:
        st.markdown("""
        <div class="empty-state">
            <div class="icon">📊</div>
            <div class="title">暂无问诊记录</div>
            <div class="desc">请先在「📋 智能问诊」中诊断并保存记录</div>
        </div>
        """, unsafe_allow_html=True)
        return

    col_left, col_right = st.columns(2)

    # 统一调色板（绿-琥珀-蓝-紫）
    palette = ['#0F7A6A', '#D4A24A', '#3A6B9E', '#7A4E8C', '#4FAE7A', '#E0A24A', '#5A7BB8', '#9B6BA5']

    with col_left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><div class="ti">🩺</div>证型分布</div>', unsafe_allow_html=True)
        syndromes = [r["syndrome"] for r in records if r.get("confidence", 0) > 0]
        if syndromes:
            df = pd.DataFrame({"证型": syndromes}).value_counts().reset_index()
            df.columns = ["证型", "数量"]
            fig = px.pie(df, names="证型", values="数量", color_discrete_sequence=palette)
            fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=11)
            fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=340,
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              font=dict(family='Noto Sans SC'))
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><div class="ti">📚</div>辨证体系</div>', unsafe_allow_html=True)
        cats = [r.get("syndrome_category", "") for r in records if r.get("syndrome_category")]
        if cats:
            df = pd.DataFrame({"辨证体系": cats}).value_counts().reset_index()
            df.columns = ["辨证体系", "数量"]
            fig = px.bar(df, x="辨证体系", y="数量", color="辨证体系",
                        color_discrete_sequence=palette)
            fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=340, showlegend=False,
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              font=dict(family='Noto Sans SC'))
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title"><div class="ti">📋</div>问诊记录 · 共 {len(records)} 条</div>', unsafe_allow_html=True)
    df_list = pd.DataFrame([{
        "日期": r.get("date", "")[:10],
        "姓名": r.get("name", ""),
        "主诉": r.get("chief_complaint", "")[:30],
        "证型": r.get("syndrome", ""),
        "方剂": r.get("formula", ""),
        "置信度": f"{r.get('confidence', 0)}%",
    } for r in reversed(records)])
    st.dataframe(df_list, use_container_width=True, height=320)
    st.markdown('</div>', unsafe_allow_html=True)

def render_knowledge_tab():
    st.markdown("""
    <div class="card">
        <div class="card-title"><div class="ti">📚</div>中医知识库</div>
        <p style="color:var(--c-ink-soft); margin:0; font-size:0.9rem;">
            涵盖经典方剂、常见证型与四大辨证体系，随时查阅。
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["💊  方剂库", "🩺  证型库", "📖  辨证体系"])

    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        col1, col2, col3 = st.columns([3, 1.4, 1.4])
        with col1:
            search_formula = st.text_input("🔍 搜索方剂", placeholder="输入方剂名称或组成...", key="formula_search", label_visibility="collapsed")
        with col2:
            categories = list(set(f.get("category", "") for f in FORMULAS if f.get("category")))
            category_filter = st.selectbox("按类别", ["全部"] + sorted(categories), key="formula_category", label_visibility="collapsed")
        with col3:
            sources = list(set(f.get("source", "") for f in FORMULAS if f.get("source")))
            source_filter = st.selectbox("按来源", ["全部"] + sorted(sources), key="formula_source", label_visibility="collapsed")

        filtered = FORMULAS
        if search_formula:
            filtered = [f for f in filtered if search_formula in f.get("name", "") or search_formula in f.get("composition", "")]
        if category_filter != "全部":
            filtered = [f for f in filtered if f.get("category") == category_filter]
        if source_filter != "全部":
            filtered = [f for f in filtered if f.get("source") == source_filter]

        st.markdown(f'<p style="color:var(--c-ink-soft); font-size:0.88rem; margin:0.8rem 0">共 <b style="color:var(--c-primary)">{len(filtered)}</b> 个方剂</p>', unsafe_allow_html=True)

        if not filtered:
            st.markdown("""
            <div class="empty-state">
                <div class="icon">🔍</div>
                <div class="title">未找到匹配的方剂</div>
                <div class="desc">试试更换关键词或筛选条件</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            cards_html = '<div class="grid">'
            for f in filtered:
                name = f.get("name", "未命名")
                category = f.get("category", "")
                source = f.get("source", "")
                composition = f.get("composition", "")
                function = f.get("function", "")
                indication = f.get("indication", "")
                cards_html += f'''
                <div class="grid-card">
                    <div class="head">
                        <div class="name">📜 {name}</div>
                    </div>
                    <div class="meta">
                        {f'<span class="chip">{category}</span>' if category else ''}
                        {f'<span class="chip amber">{source}</span>' if source else ''}
                    </div>
                    <div class="body"><b>组成：</b>{composition}</div>
                    <div class="body"><b>功效：</b>{function}</div>
                    <div class="body"><b>主治：</b>{indication}</div>
                </div>
                '''
            cards_html += '</div>'
            st.markdown(cards_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        col1, col2 = st.columns([3, 1.4])
        with col1:
            search_syndrome = st.text_input("🔍 搜索证型", placeholder="输入证型或症状...", key="syndrome_search", label_visibility="collapsed")
        with col2:
            categories = list(set(s.get("category", "") for s in SYNDROMES if s.get("category")))
            category_filter = st.selectbox("按辨证体系", ["全部"] + sorted(categories), key="syndrome_category", label_visibility="collapsed")

        filtered = SYNDROMES
        if search_syndrome:
            filtered = [s for s in filtered if search_syndrome in s.get("name", "") or search_syndrome in s.get("symptoms", "")]
        if category_filter != "全部":
            filtered = [s for s in filtered if s.get("category") == category_filter]

        st.markdown(f'<p style="color:var(--c-ink-soft); font-size:0.88rem; margin:0.8rem 0">共 <b style="color:var(--c-primary)">{len(filtered)}</b> 个证型</p>', unsafe_allow_html=True)

        if not filtered:
            st.markdown("""
            <div class="empty-state">
                <div class="icon">🔍</div>
                <div class="title">未找到匹配的证型</div>
                <div class="desc">试试更换关键词或筛选条件</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            cards_html = '<div class="grid">'
            for s in filtered:
                name = s.get("name", "未命名")
                category = s.get("category", "")
                symptoms = s.get("symptoms", "")
                tongue = s.get("tongue", "")
                pulse = s.get("pulse", "")
                formula = s.get("formula", "")
                treatment = s.get("treatment", "")
                cards_html += f'''
                <div class="grid-card">
                    <div class="head">
                        <div class="name">🩺 {name}</div>
                    </div>
                    <div class="meta">{f'<span class="chip">{category}</span>' if category else ''}</div>
                    <div class="body"><b>主要症状：</b>{symptoms}</div>
                    <div class="body"><b>舌象：</b>{tongue}</div>
                    <div class="body"><b>脉象：</b>{pulse}</div>
                    <div class="body"><b>推荐方剂：</b><span style="color:var(--c-primary); font-weight:600">{formula}</span></div>
                    <div class="body"><b>治法：</b>{treatment}</div>
                </div>
                '''
            cards_html += '</div>'
            st.markdown(cards_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown("""
        <div class="card">
            <div class="card-title"><div class="ti">📖</div>辨证体系说明</div>

            <h3 style="color:var(--c-primary-dark); margin-top:1.2rem">🔄 六经辨证（《伤寒论》）</h3>
            <p style="color:var(--c-ink-soft); line-height:1.7">
            六经辨证是《伤寒论》的核心辨证体系，将外感热病分为六个阶段，是中医临床的奠基之作。
            </p>
            <table style="width:100%; border-collapse:collapse; margin-top:0.8rem; font-size:0.88rem">
                <thead>
                    <tr style="background:var(--c-primary-soft); color:var(--c-primary-dark)">
                        <th style="padding:0.6rem; text-align:left; border-radius:8px 0 0 0">经络</th>
                        <th style="padding:0.6rem; text-align:left">证型</th>
                        <th style="padding:0.6rem; text-align:left">主要表现</th>
                        <th style="padding:0.6rem; text-align:left">代表方剂</th>
                        <th style="padding:0.6rem; text-align:left; border-radius:0 8px 0 0">病机</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom:1px solid var(--c-line)"><td style="padding:0.6rem"><b>太阳</b></td><td>表证</td><td>恶寒发热、头痛身痛</td><td>麻黄汤、桂枝汤</td><td>风寒袭表</td></tr>
                    <tr style="border-bottom:1px solid var(--c-line); background:#FBFAF4"><td style="padding:0.6rem"><b>阳明</b></td><td>里实热证</td><td>但热不寒、大汗大渴</td><td>白虎汤、承气汤</td><td>里热炽盛</td></tr>
                    <tr style="border-bottom:1px solid var(--c-line)"><td style="padding:0.6rem"><b>少阳</b></td><td>半表半里</td><td>往来寒热、口苦咽干</td><td>小柴胡汤</td><td>枢机不利</td></tr>
                    <tr style="border-bottom:1px solid var(--c-line); background:#FBFAF4"><td style="padding:0.6rem"><b>太阴</b></td><td>里虚寒证</td><td>腹满吐利、喜温喜按</td><td>理中丸</td><td>脾阳不振</td></tr>
                    <tr style="border-bottom:1px solid var(--c-line)"><td style="padding:0.6rem"><b>少阴</b></td><td>心肾虚证</td><td>畏寒蜷卧或心烦不寐</td><td>四逆汤、黄连阿胶汤</td><td>心肾阳虚/阴虚</td></tr>
                    <tr><td style="padding:0.6rem"><b>厥阴</b></td><td>寒热错杂</td><td>消渴、气上撞心</td><td>乌梅丸</td><td>阴阳对峙</td></tr>
                </tbody>
            </table>

            <h3 style="color:var(--c-primary-dark); margin-top:1.5rem">🏥 脏腑辨证</h3>
            <p style="color:var(--c-ink-soft); line-height:1.7">脏腑辨证是根据脏腑的生理功能和病理特点，对疾病进行辨证的方法：</p>
            <ul style="color:var(--c-ink); line-height:1.9">
                <li><b>心系</b>：心气虚、心血虚、心火亢盛、心血瘀阻</li>
                <li><b>肝系</b>：肝气郁结、肝火上炎、肝血虚、肝阳上亢</li>
                <li><b>脾系</b>：脾气虚、脾阳虚、脾不统血、寒湿困脾、湿热蕴脾</li>
                <li><b>肺系</b>：肺气虚、肺阴虚、风寒犯肺、风热犯肺、痰热壅肺</li>
                <li><b>肾系</b>：肾阳虚、肾阴虚、肾精不足、肾不纳气</li>
            </ul>

            <h3 style="color:var(--c-primary-dark); margin-top:1.5rem">🌡️ 卫气营血辨证（温病学）</h3>
            <table style="width:100%; border-collapse:collapse; margin-top:0.8rem; font-size:0.88rem">
                <thead>
                    <tr style="background:var(--c-amber-soft); color:#8B6A2E">
                        <th style="padding:0.6rem; text-align:left; border-radius:8px 0 0 0">分期</th>
                        <th style="padding:0.6rem; text-align:left">病位</th>
                        <th style="padding:0.6rem; text-align:left">主要表现</th>
                        <th style="padding:0.6rem; text-align:left">治法</th>
                        <th style="padding:0.6rem; text-align:left; border-radius:0 8px 0 0">代表方剂</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom:1px solid var(--c-line)"><td style="padding:0.6rem"><b>卫分</b></td><td>肌表</td><td>发热微恶风寒</td><td>辛凉解表</td><td>银翘散</td></tr>
                    <tr style="border-bottom:1px solid var(--c-line); background:#FBFAF4"><td style="padding:0.6rem"><b>气分</b></td><td>脏腑</td><td>壮热不恶寒</td><td>清气泄热</td><td>白虎汤</td></tr>
                    <tr style="border-bottom:1px solid var(--c-line)"><td style="padding:0.6rem"><b>营分</b></td><td>营阴</td><td>身热夜甚、心烦</td><td>清营透热</td><td>清营汤</td></tr>
                    <tr><td style="padding:0.6rem"><b>血分</b></td><td>血分</td><td>出血、发斑</td><td>凉血散血</td><td>犀角地黄汤</td></tr>
                </tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)

def render_herb_tab():
    st.markdown("""
    <div class="card">
        <div class="card-title"><div class="ti">🌿</div>中药库</div>
        <p style="color:var(--c-ink-soft); margin:0; font-size:0.9rem;">
            按药性、药味、归经筛选常用中药，支持搜索定位。
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns([3, 1.4, 1.4, 1.4])
    with col1:
        search = st.text_input("🔍 搜索中药", placeholder="输入药名搜索...", key="herb_search_v2", label_visibility="collapsed")
    with col2:
        natures = sorted(list(set(h.get("nature", "") for h in HERBS if h.get("nature"))))
        nature_filter = st.selectbox("药性", ["全部"] + natures, key="herb_nature_v2", label_visibility="collapsed")
    with col3:
        flavors = sorted(list(set(h.get("flavor", "") for h in HERBS if h.get("flavor"))))
        flavor_filter = st.selectbox("药味", ["全部"] + flavors, key="herb_flavor_v2", label_visibility="collapsed")
    with col4:
        # 兼容两种字段名：meridian_tropism（新）/meridian（旧）
        def _herb_meridian(h):
            return h.get("meridian_tropism") or h.get("meridian") or ""
        meridians = sorted(list(set(_herb_meridian(h) for h in HERBS if _herb_meridian(h))))
        meridian_filter = st.selectbox("归经", ["全部"] + meridians, key="herb_meridian_v2", label_visibility="collapsed")

    filtered = HERBS
    if search:
        filtered = [h for h in filtered if search in h.get("name", "")]
    if nature_filter != "全部":
        filtered = [h for h in filtered if h.get("nature") == nature_filter]
    if flavor_filter != "全部":
        filtered = [h for h in filtered if flavor_filter in h.get("flavor", "")]
    if meridian_filter != "全部":
        filtered = [h for h in filtered if _herb_meridian(h) == meridian_filter]

    st.markdown(f'<p style="color:var(--c-ink-soft); font-size:0.88rem; margin:0.8rem 0">共 <b style="color:var(--c-primary)">{len(filtered)}</b> 味中药</p>', unsafe_allow_html=True)

    if not filtered:
        st.markdown("""
        <div class="empty-state">
            <div class="icon">🔍</div>
            <div class="title">未找到匹配的中药</div>
            <div class="desc">试试更换关键词或筛选条件</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        cards_html = '<div class="grid">'
        for h in filtered:
            name = h.get("name", "未命名")
            nature = h.get("nature", "—") or "—"
            flavor = h.get("flavor", "—") or "—"
            meridian = _herb_meridian(h) or "—"
            dosage = h.get("dosage", "—") or "—"
            function = h.get("function", "—") or "—"
            # caution 是禁忌（数据里是这个 key），不是 contraindication
            caution = h.get("caution") or h.get("contraindication") or "—"
            indication = h.get("indication", "—") or "—"
            cards_html += f'''
            <div class="grid-card">
                <div class="head">
                    <div class="name">🌿 {name}</div>
                </div>
                <div class="meta">
                    <span class="chip">性 {nature}</span>
                    <span class="chip">味 {flavor}</span>
                    <span class="chip amber">{meridian}</span>
                </div>
                <div class="body"><b>用量：</b>{dosage}</div>
                <div class="body"><b>功效：</b>{function}</div>
                <div class="body"><b>主治：</b>{indication}</div>
                <div class="body"><b>使用注意：</b>{caution}</div>
            </div>
            '''
        cards_html += '</div>'
        st.markdown(cards_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_settings_tab():
    """系统设置 Tab——所有 API Key 相关显示均与当前输入同步。"""
    st.markdown("""
    <div class="card">
        <div class="card-title"><div class="ti">⚙️</div>系统设置</div>
        <p style="color:var(--c-ink-soft); margin:0; font-size:0.9rem;">
            配置 AI 引擎、查看数据存储状态、管理本地问诊记录。
        </p>
    </div>
    """, unsafe_allow_html=True)

    settings = load_settings()
    saved_key = (settings.get("api_key") or "").strip()
    saved_provider = settings.get("provider", DEFAULT_PROVIDER)
    saved_model = settings.get("model", "")

    # ===== API 配置 =====
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title"><div class="ti">🔑</div>AI 引擎配置</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:var(--c-ink-soft); font-size:0.88rem; margin:0 0 1rem 0">配置 API Key 后即可使用 AI 智能诊断功能。推荐使用 DeepSeek，价格实惠且效果好。</p>', unsafe_allow_html=True)

    provider_list = list(API_PROVIDERS.keys())
    provider_idx = provider_list.index(saved_provider) if saved_provider in provider_list else 0

    col1, col2 = st.columns(2)
    with col1:
        provider = st.selectbox("选择 API 厂商", provider_list, index=provider_idx, key="cfg_provider")
    with col2:
        provider_config = API_PROVIDERS[provider]
        models = provider_config["models"]
        cur_model = saved_model or provider_config["default_model"]
        model_idx = models.index(cur_model) if cur_model in models else 0
        model = st.selectbox("选择模型", models, index=model_idx, key="cfg_model")

    st.caption(f"📡 API 地址：{provider_config['base_url']}")

    # API Key 输入框（value 用已保存的值初始化；用户输入后由 widget key 自动持久化）
    api_key = st.text_input(
        "API Key", type="password",
        placeholder="请输入你的 API Key（DeepSeek 以 sk- 开头）",
        value=saved_key if saved_key else "",
        key="cfg_api_key"
    )

    # ★ 与输入同步的状态徽章（放在输入框下方，读的是当前 widget 值）
    _key_ok = bool(api_key and len(api_key) >= 10)
    if _key_ok:
        st.success("✅  API Key 格式有效（点击「保存配置」后生效）")
    else:
        st.warning("⚠️  请填写 API Key（长度不少于 10 个字符）")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💾  保存配置", type="primary", use_container_width=True):
            if not _key_ok:
                st.error("❌ 请输入有效的 API Key")
            else:
                new_settings = {"api_key": api_key, "provider": provider, "model": model}
                save_settings(new_settings)
                # 立刻更新 session_state，保证 Hero / 状态卡同步刷新
                st.session_state.engine = TCMDiagnosisEngine(api_key, provider, model)
                st.session_state.engine_key = f"{provider}:{api_key}"
                st.session_state._api_key_ok = True
                st.success(f"✅ 配置已保存：{provider} / {model}")
                st.rerun()
    with col2:
        if st.button("🧪  测试连接", use_container_width=True):
            if not _key_ok:
                st.error("❌ 请先输入 API Key")
            else:
                with st.spinner("测试中..."):
                    try:
                        test_engine = TCMDiagnosisEngine(api_key, provider, model)
                        if not getattr(test_engine, "has_api_key", False):
                            st.error("连接失败")
                        else:
                            result = test_engine.analyze_symptoms("测试主诉：头痛", [], "", "")
                            if isinstance(result, dict):
                                conf = result.get("confidence", 0)
                                cat = result.get("syndrome_category", "")
                                if conf > 0 and "配置错误" not in cat and "网络错误" not in cat and "限流" not in cat:
                                    st.success("连接成功")
                                else:
                                    st.error("连接失败")
                            else:
                                st.error("连接失败")
                    except Exception:
                        st.error("连接失败")
    with col3:
        if st.button("🗑️  清除配置", use_container_width=True):
            save_settings({"api_key": "", "provider": DEFAULT_PROVIDER, "model": ""})
            st.session_state.engine = TCMDiagnosisEngine()
            st.session_state.engine_key = f"{DEFAULT_PROVIDER}:"
            st.session_state._api_key_ok = False
            st.info("已清除配置")
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ===== 系统状态（读 session_state 引擎 + 当前 widget 值，保证同步）=====
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title"><div class="ti">📊</div>系统状态</div>', unsafe_allow_html=True)

    # ★ 三路判定：engine 对象 / 保存标志位 / 当前输入框值 — 任一为真即「已配置」
    _cur_engine = st.session_state.get("engine")
    _widget_key_ok = bool(api_key and len(api_key.strip()) >= 10)
    _engine_ok = (
        bool(getattr(_cur_engine, "has_api_key", False))
        or st.session_state.get("_api_key_ok", False)
        or _widget_key_ok
    )

    s1, s2 = st.columns(2)
    with s1:
        if _engine_ok:
            # 显示当前 selectbox 的值（而非磁盘快照），保证同步
            st.success(f"🔑 AI 引擎：{provider} / {model}")
        else:
            st.warning("⚠️ AI 引擎：未配置 API Key")
    with s2:
        if supabase_configured():
            st.success("☁️ 数据存储：Supabase 云端（重启不丢失）")
        else:
            st.warning("💾 数据存储：本地 JSON（重启可能丢失）")

    if not _engine_ok:
        st.info("💡 请先配置 API Key 才能使用 AI 智能诊断功能")
    if not supabase_configured():
        st.info("💡 推荐配置 Supabase 云端数据库，重启后数据不丢失（详见 `supabase/README.md`）")
    # DeepSeek Key 格式提示（用当前输入框的值判断，而非磁盘快照）
    if _key_ok and provider == "DeepSeek":
        cur = (api_key or "").strip()
        if not cur.startswith("sk-"):
            st.warning("⚠️ DeepSeek 的 API Key 通常以 `sk-` 开头，请确认 Key 是否完整（不要漏字符）")
        elif len(cur) < 30:
            st.warning("⚠️ API Key 看起来太短，DeepSeek Key 一般 30+ 字符，请检查是否复制完整")
    with st.expander("💳 DeepSeek API 余额 / Key 状态说明", expanded=False):
        st.markdown("""
- **登录控制台**：[https://platform.deepseek.com/](https://platform.deepseek.com/) → 顶部右上角「API Keys」
- **查看余额**：左侧菜单「余额」可看剩余金额；新注册一般有赠额，过期/用完会 402
- **常见 401 原因**：Key 复制时漏字符 / 多空格 / 已删除 / 已重置
- **常见 402 原因**：账号余额不足，去控制台充值即可
- **常见 429 原因**：请求过快，免费档限速 1 次/秒
- **网络问题**：Streamlit Cloud 服务器在海外，连 `api.deepseek.com` 偶有抖动，重试或换时段
        """)
    st.markdown('</div>', unsafe_allow_html=True)

    # ===== 数据管理 =====
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title"><div class="ti">🗄️</div>数据管理</div>', unsafe_allow_html=True)
    records = load_records()
    st.markdown(f'<p style="font-size:0.95rem; margin:0 0 1rem 0">当前共有 <b style="color:var(--c-primary)">{len(records)}</b> 条问诊记录</p>', unsafe_allow_html=True)

    # ★ Supabase 连接诊断按钮
    if supabase_configured():
        if st.button("🔍 诊断 Supabase 连接", use_container_width=True):
            try:
                from utils.supabase_client import diagnose_connection
                with st.spinner("正在诊断..."):
                    diag = diagnose_connection()
                if diag["errors"]:
                    for err in diag["errors"]:
                        st.error(err)
                else:
                    st.success("✅ Supabase 连接正常，表结构完整，读写测试通过")
                with st.expander("📋 诊断详情", expanded=bool(diag["errors"])):
                    st.json({
                        "已配置": diag["configured"],
                        "客户端OK": diag["client_ok"],
                        "表存在": diag["table_exists"],
                        "检测到的列": diag["columns"],
                        "缺失的列": diag["missing_columns"],
                    "记录数": diag["record_count"],
                    "测试写入": "成功" if diag["test_insert_ok"] else f"失败：{diag['test_insert_error']}",
                })
                if diag["missing_columns"]:
                    st.warning(f"缺失字段：{', '.join(diag['missing_columns'])} → 请执行 `supabase/migration_p1_session.sql`")
            except ImportError as e:
                st.error(f"❌ 导入诊断模块失败：{str(e)[:200]}")
            except Exception as e:
                st.error(f"❌ 诊断过程异常：{str(e)[:200]}")

    if st.button("🗑️  清空所有记录", use_container_width=True):
        if supabase_configured():
            ok = _sb_clear_records()
            if ok:
                st.success("已清空云端记录")
            else:
                st.error("❌ 清空失败，请检查 Supabase 配置")
        else:
            save_records([])
            st.success("已清空")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
