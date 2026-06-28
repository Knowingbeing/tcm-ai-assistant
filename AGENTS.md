# AGENTS.md — Codex 项目上下文

> 本文件由 Codex CLI 自动读取，提供完整项目上下文。
> 最后更新：2026-06-28 | 当前 commit：`4e89f96`

---

## 一、项目身份卡

| 属性 | 值 |
|------|-----|
| 项目名称 | 中医AI智能问诊助手 |
| 本地路径 | `D:\用户文件勿删\Desktop\中医AI智能问诊助手` |
| GitHub | `https://github.com/shenjianwei/tcm-ai-assistant.git` |
| 技术栈 | Python 3.12+ / Streamlit 1.30+ / Supabase / OpenAI SDK |
| 部署方式 | Streamlit Cloud（自动从 GitHub main 分支部署） |
| 作者 | 沈建伟（厦门大学 邹至庄经济研究院 数量经济学硕士 / 医学院 中医学本科） |
| 当前版本 | v2.1（十问歌结构化表单 + AI 辨证） |
| 代码规模 | app.py 1741 行 / utils 3 模块 / data 2 模块 |

**这是 Python 项目，不是 TypeScript/Node 项目。不要提议迁移到 TS。**

---

## 二、项目目标

基于 LLM 的中医智能问诊系统，实现「症状采集 → AI 辨证 → 方剂推荐」的完整流程：

1. **十问歌结构化表单**：寒热/出汗/头身/胸腹/饮食/大小便/睡眠/情志等分项填写
2. **AI 辨证引擎**：调用大模型（DeepSeek 推荐，支持 7 家厂商）输出证型+方剂+治法
3. **双存储后端**：Supabase 云端优先，JSON 本地兜底
4. **数据分析看板**：证型分布饼图、辨证体系柱状图、记录表格
5. **中医知识库**：60+ 方剂、50+ 证型、50+ 中药，支持搜索和筛选

---

## 三、核心架构

### 文件结构

```
中医AI智能问诊助手/
├── app.py                         # Streamlit 主应用（1741 行）— UI + 业务逻辑
├── app_backup.py                  # v1.x 旧版备份（多轮问诊，不再维护）
├── streamlit_app.py               # Streamlit Cloud 入口（指向 app.py）
├── requirements.txt               # Python 依赖
├── README.md                      # 项目说明
├── .streamlit/
│   ├── config.toml                # Streamlit 主题配置（清新山水风）
│   └── secrets.toml.example       # secrets 模板
├── data/
│   ├── tcm_data.py                # 方剂/证型/中药知识库（FORMULAS, SYNDROMES, HERBS）
│   ├── ten_asks.py                # 十问歌结构化数据（TEN_ASKS, ALL_ASKS, DEFAULT_TEN_ASKS）
│   ├── tcm_records.json           # 本地问诊记录（JSON 兜底）
│   └── tcm_settings.json          # 本地用户配置（JSON 兜底）
├── utils/
│   ├── llm_engine.py              # AI 辨证引擎（TCMDiagnosisEngine 类，505 行）
│   ├── supabase_client.py         # Supabase 客户端封装（471 行）
│   ├── llm_engine_backup.py       # 旧版备份
│   └── database.py                # SQLite 旧版数据库（已弃用，保留兼容）
├── supabase/
│   ├── schema.sql                 # Supabase 表结构（consultations / patients / settings）
│   └── migration_p1_session.sql   # 多轮会话字段迁移脚本
├── scripts/
│   ├── smoke_test.py              # 冒烟测试（11 段检查）
│   └── migrate_json_to_supabase.py # JSON → Supabase 迁移脚本
└── .workbuddy/
    └── memory/                    # AI 工作记忆日志
```

### 数据流

```
用户填写十问歌表单
    ↓
_collect_symptoms_from_ten_asks(sess)  ← 从 sess["ten_asks_data"] + sess["symptoms"] 收集
    ↓
engine.analyze_symptoms(chief, symptoms, tongue, pulse)  ← 调用 LLM API
    ↓
返回 {syndrome, syndrome_category, formula, confidence, ...}
    ↓
_save_chat_session(sess)  ← 写入 Supabase 或 JSON
    ↓
load_records.clear()  ← 清除缓存，数据分析 Tab 立即可见
```

### 存储双后端

- **Supabase 模式**（优先）：`supabase_configured()` 返回 True 时，所有读写走 Supabase
  - 凭证来源：`.streamlit/secrets.toml` > 环境变量 > 无配置
  - 表：`consultations`（问诊记录）、`settings`（用户配置）
  - `save_record()` 返回 `(bool, str)` 元组，第二个值是错误详情
  - `get_records()` 有排序降级：`created_at desc` → `id desc` → 无排序
- **JSON 兜底**：Supabase 未配置时，读写 `data/tcm_records.json` / `data/tcm_settings.json`
  - `DATA_DIR = os.path.join(_APP_DIR, "data")` — 始终用项目级目录，不用 `/tmp`

### AI 引擎

- **TCMDiagnosisEngine**（`utils/llm_engine.py`）：支持 7 家厂商
  - DeepSeek（推荐）、OpenAI、通义千问、文心一言、讯飞星火、智谱 GLM、Moonshot
  - 自动识别 Key 前缀判断厂商，也支持手动选择
  - `analyze_symptoms()` 是核心方法：传入主诉+症状+舌象+脉象，返回辨证结果 dict
- **API Key 四路判定**（`app.py` line 596-601）：
  1. `st.session_state.get("_api_key_ok", False)` — 保存按钮标志位
  2. `getattr(engine, "has_api_key", False)` — engine 对象
  3. 磁盘/云端 settings 中的 key
  4. 当前输入框 widget 值

### UI 设计系统

- **清新山水风格**：主色荷绿 `#0F7A6A`，辅色琥珀 `#D4A24A`，背景米白 `#FAF8F3`
- CSS 变量定义在 `app.py` 顶部 `<style>` 块（line 38-486）
- 4 个 Tab：📋 智能问诊 / 📊 数据分析 / 📚 知识库 / 🌿 中药库 / ⚙️ 系统设置
- 所有自定义样式通过 `st.markdown(..., unsafe_allow_html=True)` 注入

---

## 四、不要破坏的函数签名

以下函数被多处调用，修改签名会引发连锁故障：

```python
# app.py
def load_records() -> list[dict]                    # @st.cache_data(ttl=30) 装饰
def save_records(records: list[dict]) -> None
def load_settings() -> dict
def save_settings(settings: dict) -> None
def get_engine() -> TCMDiagnosisEngine
def supabase_configured() -> bool                   # 从 utils 导入的别名
def _sb_save_record(record: dict) -> tuple[bool, str]
def _collect_symptoms_from_ten_asks(sess: dict) -> list[str]

# utils/supabase_client.py
def save_record(record: dict) -> tuple[bool, str]   # 返回 (成功?, 错误信息)
def get_records() -> list[dict]
def diagnose_connection() -> dict
def _format_supabase_error(e: Exception) -> str

# utils/llm_engine.py
class TCMDiagnosisEngine:
    def analyze_symptoms(self, chief, symptoms, tongue, pulse) -> dict
```

---

## 五、当前状态与已知问题

### 已完成的修复（v1.0 → v2.1）

1. ✅ Supabase 双后端持久化
2. ✅ `@st.cache_data(ttl=30)` + `load_records.clear()` 缓存刷新
3. ✅ `save_record` 返回 `(bool, str)` 错误透传
4. ✅ API Key 四路判定 + `.get()` 容错
5. ✅ Supabase 诊断面板（设置 Tab）
6. ✅ 保存失败展开排查建议
7. ✅ `_collect_symptoms_from_ten_asks` 键名修复（`ten_asks` → `ten_asks_data`）
8. ✅ 死代码清理（删除 5 个多轮问诊遗留函数）
9. ✅ README.md 全面更新

### 已知的技术债务

1. **`app.py` 过大**（1741 行）：UI + 业务逻辑 + 数据层混在一起，未来应拆分
2. **`app_backup.py` / `llm_engine_backup.py`**：旧版备份文件仍在仓库中，应择机清理
3. **`utils/database.py`**：SQLite 旧版数据库模块，已弃用但仍保留
4. **`Dockerfile`**：项目已改用 Streamlit Cloud 部署，Dockerfile 过时

### 待开发功能（按优先级）

1. **多轮深度问诊**：根据辨证结果追问 2-3 个问题，提高准确率
2. **ChromaDB 向量检索**：证型/方剂语义搜索
3. **病历导出**：PDF / Word 格式
4. **移动端适配**：响应式布局优化

---

## 六、开发约定

### 代码风格

- 使用中文注释和 docstring
- 变量命名：英文 snake_case
- CSS 类名：kebab-case
- 常量：UPPER_SNAKE_CASE
- 不要使用 `any` 类型（这是 Python 项目，用 `typing` 模块）

### Git 约定

- 分支：直接在 `main` 上开发（个人项目，无 PR 流程）
- commit message 格式：`type: 描述`（type = feat/fix/refactor/docs/chore）
- **沙箱环境无法 `git push`**（需要交互式 GitHub 认证）— 提交后告知用户在本地终端推送

### 验证流程（每次修改后必须执行）

```bash
# 1. AST 语法检查
python -c "import ast; ast.parse(open('app.py', encoding='utf-8').read()); print('[OK]')"

# 2. 冒烟测试（需要安装 streamlit）
python scripts/smoke_test.py
```

### Supabase 排错 SOP

如果用户报告「保存失败」或「数据看不到」：

1. **检查 `secrets.toml`**：确认 `SUPABASE_URL` 和 `SUPABASE_KEY` 已配置
2. **运行诊断面板**：系统设置 Tab → 「🔍 诊断 Supabase 连接」按钮
3. **常见原因（按频率排序）**：
   - RLS 拦截 → `ALTER TABLE consultations DISABLE ROW LEVEL SECURITY;`
   - 表不存在 → 执行 `supabase/schema.sql`
   - 缺字段 → 执行 `supabase/migration_p1_session.sql`
   - CHECK 约束 → 检查 confidence (0-100)、gender ('男'/'女')、source 值
   - Key 无效 → 检查 secrets.toml 中的值

---

## 七、绝对不要做的事

1. **不要把项目改成 TypeScript** — 这是 Python/Streamlit 项目
2. **不要删除 `_sb_save_record` 的 `(bool, str)` 返回格式** — UI 依赖错误信息透传
3. **不要移除 `@st.cache_data(ttl=30)` 装饰器** — 保存后数据看不到会复发
4. **不要把 `DATA_DIR` 改回 `/tmp`** — Streamlit Cloud 重启会丢数据
5. **不要用 `st.session_state._api_key_ok` 直接属性访问** — 用 `.get()` 容错
6. **不要在 `get_records()` 中直接用 `.order("created_at")` 不加 try/except** — 表可能缺该列

---

## 八、用户偏好

- 使用中文回答
- 小步快跑：改一点验证一点，不要一次性大改
- 每次修改后跑 AST 检查确认语法合法
- commit message 用中文描述
- 遇到 Supabase 问题优先用诊断面板定位，不要盲目改代码
- 推送代码需要用户在本地终端执行（沙箱无交互式 GitHub 认证）

---

## 九、接手确认

读完本文件后，请回复以下信息确认已掌握上下文：

1. 当前项目版本和 commit hash
2. `_collect_symptoms_from_ten_asks` 从哪个 session_state 键读取十问歌数据
3. `save_record` 的返回值类型
4. API Key 四路判定分别是哪四路
5. Supabase 排错时最常见的失败原因
