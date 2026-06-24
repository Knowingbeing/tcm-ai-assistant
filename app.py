import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(__file__))
from utils.database import get_connection, init_database, insert_sample_data
from utils.llm_engine import TCMDiagnosisEngine, API_PROVIDERS

st.set_page_config(
    page_title="中医AI智能问诊助手",
    page_icon="🏥",
    layout="wide"
)

def init_db():
    init_database()
    insert_sample_data()

def get_engine():
    api_key = st.session_state.get("api_key", "")
    provider = st.session_state.get("api_provider", "OpenAI")
    model = st.session_state.get("api_model", "")
    engine_key = f"{provider}:{api_key}"
    if "engine" not in st.session_state or st.session_state.get("engine_key") != engine_key:
        st.session_state.engine = TCMDiagnosisEngine(api_key, provider, model)
        st.session_state.engine_key = engine_key
    return st.session_state.engine

def main():
    init_db()
    engine = get_engine()

    st.title("🏥 中医AI智能问诊助手")
    st.markdown("---")

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
    st.header("智能问诊")

    col1, col2 = st.columns([2, 3])

    with col1:
        st.subheader("患者信息")
        patient_name = st.text_input("姓名", placeholder="请输入患者姓名")
        patient_age = st.number_input("年龄", min_value=0, max_value=150, value=30)
        patient_gender = st.selectbox("性别", ["男", "女"])

        st.subheader("问诊信息")
        chief_complaint = st.text_area("主诉", placeholder="请描述主要症状，如：头痛、发热3天", height=100)

        st.subheader("症状选择")
        try:
            conn = get_connection()
            df_symptoms = pd.read_sql("SELECT symptom_name FROM symptoms ORDER BY category, symptom_name", conn)
            all_symptoms = df_symptoms['symptom_name'].tolist()
        except Exception:
            all_symptoms = ["发热", "恶寒", "头痛", "咳嗽", "鼻塞", "流涕", "咽喉痛",
                          "胸闷", "心悸", "腹痛", "腹泻", "便秘", "食欲不振", "口渴",
                          "口苦", "失眠", "乏力", "自汗", "腰膝酸软", "畏寒肢冷"]
        selected_symptoms = st.multiselect("请选择伴随症状", all_symptoms)

        st.subheader("舌脉信息")
        tongue_sign = st.text_input("舌象", placeholder="如：舌苔薄白、舌质淡红")
        pulse_sign = st.text_input("脉象", placeholder="如：脉浮紧、脉弦细")

    with col2:
        st.subheader("AI诊断结果")

        if st.button("🔍 开始诊断", type="primary", use_container_width=True):
            if not chief_complaint:
                st.error("请输入主诉信息")
            else:
                with st.spinner("AI正在分析中..."):
                    result = engine.analyze_symptoms(
                        chief_complaint, selected_symptoms, tongue_sign, pulse_sign
                    )

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
                        st.markdown("**加减建议**")
                        st.warning(result["formula_adjustment"])

                if result.get("additional_notes"):
                    st.markdown("#### 提示")
                    if result["confidence"] > 0:
                        st.warning(result["additional_notes"])
                    else:
                        st.error(result["additional_notes"])

                if st.button("💾 保存问诊记录"):
                    if save_consultation(patient_name, patient_age, patient_gender,
                                     chief_complaint, selected_symptoms, tongue_sign,
                                     pulse_sign, result):
                        st.success("✅ 问诊记录已保存！可在「数据分析」查看")

def save_consultation(name, age, gender, chief_complaint, symptoms, tongue, pulse, result):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO patients (name, gender, age) VALUES (?, ?, ?)
    """, (name, gender, age))
    patient_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO consultations (patient_id, chief_complaint, symptom_description,
                                  tongue_sign, pulse_sign, ai_confidence)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (patient_id, chief_complaint, ', '.join(symptoms), tongue, pulse, result['confidence']))
    consultation_id = cursor.lastrowid

    for symptom in symptoms:
        cursor.execute("""
            INSERT OR IGNORE INTO consultation_symptoms (consultation_id, symptom_id)
            SELECT ?, symptom_id FROM symptoms WHERE symptom_name = ?
        """, (consultation_id, symptom))

    conn.commit()
    return True

def render_analytics_tab():
    st.header("数据分析看板")

    try:
        conn = get_connection()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_patients = pd.read_sql("SELECT COUNT(*) as cnt FROM patients", conn).iloc[0, 0]
            st.metric("总患者数", total_patients)
        with col2:
            total_consultations = pd.read_sql("SELECT COUNT(*) as cnt FROM consultations", conn).iloc[0, 0]
            st.metric("总问诊数", total_consultations)
        with col3:
            avg_confidence = pd.read_sql("SELECT AVG(ai_confidence) as avg_conf FROM consultations WHERE ai_confidence > 0", conn).iloc[0, 0]
            st.metric("平均置信度", f"{avg_confidence:.1f}%" if avg_confidence else "N/A")
        with col4:
            confirmed = pd.read_sql("SELECT COUNT(*) as cnt FROM consultations WHERE doctor_confirmed = 1", conn).iloc[0, 0]
            st.metric("医生确认数", confirmed)

        st.markdown("---")

        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("问诊趋势（近30天）")
            df_trend = pd.read_sql("""
                SELECT DATE(consultation_date) as date, COUNT(*) as count
                FROM consultations
                WHERE consultation_date >= date('now', '-30 days')
                GROUP BY DATE(consultation_date)
                ORDER BY date
            """, conn)

            if not df_trend.empty:
                fig_trend = px.line(df_trend, x='date', y='count', title="每日问诊量")
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.info("暂无数据")

        with col_right:
            st.subheader("证型分布")
            df_syndrome = pd.read_sql("""
                SELECT s.syndrome_name, COUNT(*) as count
                FROM consultations c
                JOIN syndromes s ON c.ai_diagnosed_syndrome_id = s.syndrome_id
                GROUP BY s.syndrome_name
                ORDER BY count DESC
            """, conn)

            if not df_syndrome.empty:
                fig_syndrome = px.pie(df_syndrome, names='syndrome_name', values='count', title="证型分布")
                st.plotly_chart(fig_syndrome, use_container_width=True)
            else:
                st.info("暂无数据")

        st.markdown("---")

        st.subheader("症状频率统计")
        df_symptoms = pd.read_sql("""
            SELECT symptom_name, COUNT(*) as frequency
            FROM consultation_symptoms cs
            JOIN symptoms s ON cs.symptom_id = s.symptom_id
            GROUP BY symptom_name
            ORDER BY frequency DESC
            LIMIT 10
        """, conn)

        if not df_symptoms.empty:
            fig_symptoms = px.bar(df_symptoms, x='symptom_name', y='frequency', title="Top 10 症状频率")
            st.plotly_chart(fig_symptoms, use_container_width=True)
        else:
            st.info("暂无数据")

        st.markdown("---")

        st.subheader("证型分类统计")
        df_category = pd.read_sql("""
            SELECT s.category, COUNT(*) as count
            FROM consultations c
            JOIN syndromes s ON c.ai_diagnosed_syndrome_id = s.syndrome_id
            GROUP BY s.category
            ORDER BY count DESC
        """, conn)

        if not df_category.empty:
            fig_category = px.bar(df_category, x='category', y='count', title="证型分类分布", color='category')
            st.plotly_chart(fig_category, use_container_width=True)
        else:
            st.info("暂无数据")

    except Exception as e:
        st.error(f"数据分析加载失败：{str(e)}")
        st.info("请确保数据库已正确初始化")

def render_knowledge_tab():
    st.header("中医知识库")

    tab1, tab2, tab3, tab4 = st.tabs(["方剂库", "证型库", "辨证体系", "经典条文"])

    conn = get_connection()

    with tab1:
        st.subheader("常用方剂")
        category_filter = st.selectbox("按类别筛选", ["全部", "经方", "和解剂", "补益剂", "清热剂", "理气剂", "理血剂", "祛湿剂", "祛痰剂", "安神剂", "固涩剂", "解表剂", "泻下剂", "温里剂", "治风剂", "治燥剂"])
        
        if category_filter == "全部":
            df_formulas = pd.read_sql("SELECT * FROM formulas ORDER BY source_book, formula_name", conn)
        else:
            df_formulas = pd.read_sql(f"SELECT * FROM formulas WHERE category = '{category_filter}' ORDER BY formula_name", conn)
        
        if not df_formulas.empty:
            for _, row in df_formulas.iterrows():
                with st.expander(f"📜 {row['formula_name']} [{row['category']}] - {row['source_book']}"):
                    st.write(f"**组成**：{row['composition']}")
                    st.write(f"**功效**：{row['function']}")
                    st.write(f"**主治**：{row['indication']}")
        else:
            st.info("方剂库为空，请先初始化数据")

    with tab2:
        st.subheader("证型分类")
        category_filter2 = st.selectbox("按辨证体系筛选", ["全部", "六经辨证", "脏腑辨证", "气血津液辨证", "卫气营血辨证", "三焦辨证", "痹证"])
        
        if category_filter2 == "全部":
            df_syndromes = pd.read_sql("SELECT * FROM syndromes ORDER BY category, syndrome_name", conn)
        else:
            df_syndromes = pd.read_sql(f"SELECT * FROM syndromes WHERE category = '{category_filter2}' ORDER BY sub_category, syndrome_name", conn)
        
        if not df_syndromes.empty:
            for _, row in df_syndromes.iterrows():
                with st.expander(f"🩺 {row['syndrome_name']} [{row['sub_category']}]"):
                    st.write(f"**定义**：{row['description']}")
                    st.write(f"**常见症状**：{row['common_symptoms']}")
                    st.write(f"**舌象**：{row['tongue_sign']}")
                    st.write(f"**脉象**：{row['pulse_sign']}")
                    st.write(f"**治法**：{row['treatment_principle']}")
                    st.write(f"**来源**：{row['source']}")
        else:
            st.info("证型库为空，请先初始化数据")

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

        ### 卫气营血辨证（温病学）
        - **卫分证**：温邪初袭，发热微恶风寒
        - **气分证**：邪热亢盛，壮热不恶寒
        - **营分证**：热灼营阴，身热夜甚
        - **血分证**：热盛动血，出血发斑

        ### 三焦辨证（温病学）
        - **上焦**：肺卫证候
        - **中焦**：脾胃证候
        - **下焦**：肝肾证候
        """)

    with tab4:
        st.subheader("经典条文")
        st.markdown("""
        ### 《伤寒论》经典条文

        **第1条**：太阳之为病，脉浮，头项强痛而恶寒。

        **第2条**：太阳病，发热，汗出，恶风，脉缓者，名为中风。

        **第3条**：太阳病，或已发热，或未发热，必恶寒，体痛，呕逆，脉阴阳俱紧者，名为伤寒。

        **第12条**：太阳中风，阳浮而阴弱，阳浮者，热自发；阴弱者，汗自出。啬啬恶寒，淅淅恶风，翕翕发热，鼻鸣干呕者，桂枝汤主之。

        **第35条**：太阳病，头痛发热，身疼腰痛，骨节疼痛，恶风，无汗而喘者，麻黄汤主之。

        **第96条**：伤寒五六日中风，往来寒热，胸胁苦满，嘿嘿不欲饮食，心烦喜呕，或胸中烦而不呕，或渴，或腹中痛，或胁下痞硬，或心下悸、小便不利，或不渴、身有微热，或咳者，小柴胡汤主之。

        **第176条**：伤寒，脉浮滑，此以表有热，里有寒，白虎汤主之。

        **第219条**：三阳合病，腹满身重，难以转侧，口不仁面垢，谵语遗尿。发汗则谵语甚。额上生汗，手足逆冷。若自汗出者，白虎汤主之。

        ### 《温病条辨》经典条文

        **上焦篇第4条**：太阴风温，但热，不恶寒而渴者，辛凉平剂银翘散主之。

        **中焦篇第1条**：面目俱赤，语声重浊，呼吸俱粗，大便闭，小便涩，舌苔老黄，甚则黑有芒刺，但恶热，不恶寒，日晡益甚者，传至中焦，阳明温病也。

        **下焦篇第1条**：风温、温热、温疫、温毒，传入下焦，劫烁真阴，或因误攻，或因妄汗，神倦瘛疭，脉气虚弱，舌绛苔少，时时欲脱者，大定风珠主之。
        """)

def render_herb_tab():
    st.header("中药库")

    conn = get_connection()

    st.subheader("中药查询")
    col1, col2 = st.columns(2)

    with col1:
        search_term = st.text_input("搜索中药", placeholder="输入中药名称")
        nature_filter = st.selectbox("按药性筛选", ["全部", "寒", "凉", "平", "温", "热"])

    with col2:
        flavor_filter = st.selectbox("按药味筛选", ["全部", "辛", "甘", "酸", "苦", "咸", "淡"])
        meridian_filter = st.selectbox("按归经筛选", ["全部", "心", "肝", "脾", "肺", "肾", "胃", "大肠", "小肠", "膀胱", "胆", "三焦"])

    query = "SELECT * FROM herbs WHERE 1=1"
    if search_term:
        query += f" AND herb_name LIKE '%{search_term}%'"
    if nature_filter != "全部":
        query += f" AND nature = '{nature_filter}'"
    if flavor_filter != "全部":
        query += f" AND flavor LIKE '%{flavor_filter}%'"
    if meridian_filter != "全部":
        query += f" AND meridian_tropism LIKE '%{meridian_filter}%'"
    query += " ORDER BY herb_name"

    df_herbs = pd.read_sql(query, conn)

    st.write(f"共找到 **{len(df_herbs)}** 味中药")

    if not df_herbs.empty:
        for _, row in df_herbs.iterrows():
            with st.expander(f"🌿 {row['herb_name']} - {row['nature']}性 {row['flavor']}味"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"**药性**：{row['nature']}")
                    st.write(f"**药味**：{row['flavor']}")
                    st.write(f"**归经**：{row['meridian_tropism']}")
                with col_b:
                    st.write(f"**功效**：{row['function']}")
                    st.write(f"**主治**：{row['indication']}")
                    st.write(f"**用量**：{row['dosage']}")
                if row['contraindication']:
                    st.warning(f"**禁忌**：{row['contraindication']}")
    else:
        st.info("未找到符合条件的中药")

def render_settings_tab():
    st.header("系统设置")

    st.subheader("API配置")
    
    col1, col2 = st.columns(2)
    with col1:
        provider = st.selectbox("选择 API 厂商", list(API_PROVIDERS.keys()),
                               index=list(API_PROVIDERS.keys()).index(st.session_state.get("api_provider", "OpenAI")))
    with col2:
        provider_config = API_PROVIDERS[provider]
        model = st.selectbox("选择模型", provider_config["models"],
                            index=provider_config["models"].index(provider_config["default_model"]) if provider_config["default_model"] in provider_config["models"] else 0)
    
    st.caption(f"📡 API 地址：{provider_config['base_url']}")
    
    current_key = st.session_state.get("api_key", "")
    api_key = st.text_input("API Key", type="password", placeholder="输入你的 API Key...", value=current_key)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💾 保存配置", type="primary"):
            if api_key and len(api_key) > 5:
                st.session_state.api_key = api_key
                st.session_state.api_provider = provider
                st.session_state.api_model = model
                st.session_state.engine = TCMDiagnosisEngine(api_key, provider, model)
                st.session_state.engine_key = f"{provider}:{api_key}"
                st.success(f"✅ 已保存 {provider} / {model}")
                st.rerun()
            else:
                st.error("❌ 请输入有效的 API Key")
    with col2:
        if st.button("🧪 测试连接"):
            if api_key and len(api_key) > 5:
                with st.spinner("测试中..."):
                    test_engine = TCMDiagnosisEngine(api_key, provider, model)
                    result = test_engine.analyze_symptoms("测试", [], "", "")
                    if result.get("confidence", 0) > 0 or "失败" not in result.get("syndrome", ""):
                        st.success("✅ 连接成功！")
                    else:
                        st.error(f"❌ {result.get('additional_notes', '连接失败')}")
            else:
                st.error("❌ 请先输入 API Key")
    with col3:
        if st.button("🗑️ 清除配置"):
            st.session_state.api_key = ""
            st.session_state.api_provider = "OpenAI"
            st.session_state.engine = TCMDiagnosisEngine("")
            st.session_state.engine_key = ""
            st.info("已切换到演示模式")
            st.rerun()
    
    st.markdown("---")
    st.subheader("当前状态")
    if current_key and len(current_key) > 5:
        st.success(f"🔑 已配置 {provider} / {model}，AI 智能诊断已启用")
    else:
        st.info("📋 演示模式（基于规则的诊断）")

    st.subheader("数据管理")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 重新初始化数据库"):
            init_database()
            insert_sample_data()
            st.success("数据库已重新初始化")
    with col2:
        conn = get_connection()
        stats = {
            "证型": pd.read_sql("SELECT COUNT(*) as cnt FROM syndromes", conn).iloc[0, 0],
            "方剂": pd.read_sql("SELECT COUNT(*) as cnt FROM formulas", conn).iloc[0, 0],
            "症状": pd.read_sql("SELECT COUNT(*) as cnt FROM symptoms", conn).iloc[0, 0],
            "中药": pd.read_sql("SELECT COUNT(*) as cnt FROM herbs", conn).iloc[0, 0],
        }
        st.write("**知识库统计**")
        for k, v in stats.items():
            st.write(f"- {k}：{v} 条")

    st.subheader("关于")
    st.info("""
    **中医AI智能问诊助手** v2.0

    基于 LLM + RAG 架构的中医智能问诊系统

    **核心功能**：
    - 症状采集与智能分析
    - AI辨证论治（支持六经/脏腑/卫气营血/三焦辨证）
    - 数据可视化看板
    - 中医知识库查询（方剂/证型/中药）
    - 经典条文查阅

    **技术栈**：
    - Streamlit (前端)
    - SQLite (数据库 - 星型模型)
    - OpenAI GPT-3.5 (AI引擎 + 中医知识库)
    - Plotly (可视化)

    **知识库规模**：
    - 证型：50+（涵盖六经辨证、脏腑辨证、气血津液辨证、卫气营血辨证）
    - 方剂：60+（经方+时方）
    - 症状：150+（含舌脉细分）
    - 中药：50+（性味归经、功效主治）
    """)

if __name__ == "__main__":
    main()
