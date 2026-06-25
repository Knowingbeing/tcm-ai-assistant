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

## 开发约定
- 中文 UI，绿色主题（#0D7C66），Noto Sans SC 字体
- 所有 LLM 调用统一走 `utils/llm_engine.TCMDiagnosisEngine.analyze_symptoms`
- 离线测试通过 `scripts/smoke_test.py`（不依赖真实凭证）
- 数据迁移走 `scripts/migrate_json_to_supabase.py`（幂等）
- 部署配置走 `.streamlit/secrets.toml`（已 gitignore），模板是 `secrets.toml.example`

## 优先级路线
- P0 ✅ Supabase 持久化（已完成，2026-06-25）
- P1 多轮问诊（追问式对话）
- P2 舌象识别 / 用户系统
