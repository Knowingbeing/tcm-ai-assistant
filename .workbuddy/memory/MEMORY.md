# 中医AI智能问诊助手 — 项目长期记忆

## 项目信息
- **路径**：`D:\用户文件勿删\Desktop\中医AI智能问诊助手\`
- **GitHub**：https://github.com/Knowingbeing/tcm-ai-assistant
- **作者**：沈建伟（厦门大学数量经济学硕士 + 中医学本科背景）
- **技术栈**：Streamlit + Python + DeepSeek/OpenAI 兼容 API + Supabase Postgres

## 架构约定
- 单租户应用，anon key 直连 Supabase，RLS 禁用
- 存储后端支持自动降级：Supabase 配置 → 走云端；未配置 → 走本地 JSON
- 知识库分方剂/证型/中药/经典条文，存于 `data/tcm_data.py`（约 50K 字符）
- 4 个核心函数 `load_records/save_records/load_settings/save_settings` 保持稳定签名，上层 UI 通过 `_row_to_record` 适配云端 schema

## UI 设计系统（清新山水风，2026-06-25 重构）
- **主色**：荷绿 `#0F7A6A` / **辅色**：琥珀 `#D4A24A` / **墨色**：`#1F2933` / **米白**：`#FAF8F3`
- 圆角 token：sm 8 / md 14 / lg 20 / xl 28
- 阴影 token：sm / md / lg
- 组件库：`.hero-wrap` 品牌区 / `.quick-grid` 快速入口 / `.card` 统一卡片 / `.grid` 知识库卡片 / `.result-stack` 诊断结果 / `.empty-state` 空态 / `.status-pill` 状态徽章
- plotly 调色板：`['#0F7A6A', '#D4A24A', '#3A6B9E', '#7A4E8C', '#4FAE7A', '#E0A24A', '#5A7BB8', '#9B6BA5']`
- sticky tabs 导航条、隐藏 streamlit 默认 header/footer/menu
- 移动端 ≤768px 响应式断点
- 关键原则：所有数据访问走 `.get(..., '—')` 兜底，缺字段不崩溃

## 开发约定
- 中文 UI，清新山水风主题，Noto Sans SC 字体
- 所有 LLM 调用统一走 `utils/llm_engine.TCMDiagnosisEngine.analyze_symptoms`
- 离线测试通过 `scripts/smoke_test.py`（不依赖真实凭证）
- 数据迁移走 `scripts/migrate_json_to_supabase.py`（幂等）
- 部署配置走 `.streamlit/secrets.toml`（已 gitignore），模板是 `secrets.toml.example`

## 优先级路线
- P0 ✅ Supabase 持久化（2026-06-25）
- P0 ✅ UI 大改版清新山水风（2026-06-25）
- P1 ✅ 多轮问诊 / 追问式对话（2026-06-25）
- P2 舌象识别 / 用户系统

## P1 多轮问诊（已完成，2026-06-25）

**用户选型**：AI 主动追问 + 智能判断追问必要性 + 轻量级 session 缓存

**架构**
- `utils/llm_engine.py` 新增 3 个方法：
  - `should_ask_followup(cc, symptoms, tongue, pulse, round) → {need_followup, questions, reason}`
  - `chat_with_history(messages, temperature=0.3)` 多轮 LLM 调用
  - `diagnose_with_conversation(session)` 完整对话版辨证
- `supabase/migration_p1_session.sql` 给 consultations 表加：
  - `session_id uuid` / `round_index int` / `messages jsonb` + 索引 `idx_session`
- `utils/supabase_client.py` 新增 `save_record / get_sessions / get_session_history`
- `app.py` 重构 `render_consultation_tab` 为聊天窗口，state 走 `st.session_state.chat_session`

**追问答案分配规则**（`_apply_followup_answer`）
- 问舌象 / 苔 → 写回 `sess["tongue_sign"]`
- 问脉象 → 写回 `sess["pulse_sign"]`
- 寒热 / 二便 / 出汗 → 追加到 `sess["symptoms"]` 列表
- 其它 → 拼到 `sess["extra_notes"]`

**问诊流程**
1. 用户填主诉 + 初始四诊 → 开始问诊
2. 走 `_maybe_diagnose` 调 LLM 判断：信息够 → `_finalize_diagnosis`；不够 → 给出 2-4 个追问选项
3. 用户点选项 / 自由输入 → `_apply_followup_answer` 写回对应字段
4. 累计到 4 轮强制收尾
5. 完成后可保存会话到 Supabase

**测试**
- `scripts/smoke_test.py` 11 段全过
- 端到端：头痛三天 → 追问舌/寒热/二便/脉 → 正确辨证
- streamlit run app.py --port 8765 HTTP 200

