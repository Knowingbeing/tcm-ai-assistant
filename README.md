# 中医 AI 智能问诊助手

基于 LLM 的中医智能问诊系统，围绕「十问歌结构化采集 → AI 辨证 → 方剂推荐 → 数据沉淀」构建完整问诊流程。

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)
![Supabase](https://img.shields.io/badge/Supabase-Cloud-3ECF8E?logo=supabase)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 项目亮点

- **十问歌结构化问诊**：寒热、汗出、头身、二便、饮食口味、睡眠、旧病、病因、女性经期等信息分阶段采集。
- **AI 辨证引擎**：支持 DeepSeek、OpenAI、通义千问、文心一言、讯飞星火、智谱 GLM、Moonshot 等 7 家厂商。
- **轻量追问闭环**：信息不足时自动追问舌象、脉象、寒热、汗出、二便等关键项，再生成最终辨证。
- **双存储后端**：Supabase 云端优先，未配置时自动回退到项目内 JSON 文件。
- **知识库一体化**：方剂库、证型库、辨证体系、中药库统一收纳在「知识库」Tab。
- **诊断与排错面板**：Supabase 连接诊断、保存失败原因透传、缓存刷新机制均已内置。

## 功能模块

### 智能问诊

- 患者基础信息、主诉、伴随症状、舌象、脉象录入
- 十问歌结构化表单辅助补全四诊信息
- 自动判断是否需要追问，最多补充关键问题后输出辨证
- 生成证型、辨证体系、治法、推荐方剂、方剂加减、置信度与注意事项

### 数据分析

- 问诊总数、有效诊断、平均置信度、最新记录
- 证型分布、辨证体系统计
- 问诊记录表格浏览
- 明确显示当前存储后端：Supabase 或本地 JSON

### 知识库

- **方剂库**：68 首经方/时方，支持名称、组成、类别、来源筛选
- **证型库**：47 个常见证型，支持证型和症状检索
- **辨证体系**：六经辨证、脏腑辨证、卫气营血辨证说明
- **中药库**：87 味中药，支持药性、药味、归经筛选

### 系统设置

- AI 厂商、模型、API Key 配置
- Supabase 存储状态和连接诊断
- 本地/云端问诊记录管理

## 技术架构

```text
Streamlit UI
    |
    |-- 智能问诊 / 数据分析 / 知识库 / 系统设置
    |
Python 业务层
    |
    |-- app.py                 页面渲染、问诊流程、数据看板
    |-- utils/llm_engine.py    LLM 辨证、追问判断、规则兜底
    |-- utils/supabase_client.py  Supabase CRUD 与诊断
    |
数据层
    |
    |-- data/tcm_data.py       方剂、证型、中药知识库
    |-- data/ten_asks.py       十问歌结构化配置
    |-- supabase/schema.sql    云端数据库结构
    |-- data/*.json            本地兜底存储
```

## 快速开始

```bash
git clone https://github.com/Knowingbeing/tcm-ai-assistant.git
cd tcm-ai-assistant

pip install -r requirements.txt
streamlit run app.py
```

应用启动后，在「系统设置」中填入 API Key 即可使用 AI 辨证。未配置 API Key 时，系统会使用规则兜底诊断，便于演示和本地测试。

## 可选配置

### Streamlit Secrets

复制 `.streamlit/secrets.toml.example` 为 `.streamlit/secrets.toml`，再填写：

```toml
DEEPSEEK_API_KEY = "sk-xxx"
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"
```

也可以直接在应用的「系统设置」Tab 中填写 API Key。

### Supabase

1. 在 Supabase 创建项目
2. 在 SQL Editor 执行 `supabase/schema.sql`
3. 如需多轮会话字段，执行 `supabase/migration_p1_session.sql`
4. 配置 `SUPABASE_URL` 和 `SUPABASE_KEY`

常见保存失败原因包括 RLS 拦截、表未创建、缺字段、CHECK 约束不匹配、Key 无效。应用内置「诊断 Supabase 连接」按钮用于定位问题。

## 项目结构

```text
tcm-ai-assistant/
├── app.py                         # Streamlit 主应用
├── streamlit_app.py               # Streamlit Cloud 入口
├── requirements.txt               # Python 依赖
├── README.md                      # GitHub 项目首页
├── AGENTS.md                      # Codex 项目上下文
├── LICENSE                        # MIT 许可证
├── .env.example                   # 环境变量示例
├── .streamlit/
│   ├── config.toml                # Streamlit 主题配置
│   └── secrets.toml.example       # secrets 模板
├── data/
│   ├── tcm_data.py                # 方剂/证型/中药知识库
│   └── ten_asks.py                # 十问歌问诊配置
├── utils/
│   ├── llm_engine.py              # AI 辨证引擎
│   ├── supabase_client.py         # Supabase 客户端
│   └── database.py                # SQLite 旧版兼容模块
├── supabase/
│   ├── schema.sql                 # Supabase 建表脚本
│   ├── migration_p1_session.sql   # 多轮会话字段迁移
│   └── README.md                  # Supabase 部署说明
├── scripts/
│   ├── smoke_test.py              # 冒烟测试
│   └── migrate_json_to_supabase.py
└── knowledge_base/                # 项目文档中心
    ├── 00_项目总览.md
    ├── 01_系统架构与数据流.md
    ├── 02_前端UI层.md
    ├── 03_存储层.md
    ├── 04_AI引擎层.md
    ├── 05_数据层.md
    ├── 06_数据库Schema.md
    ├── 07_错误处理与诊断.md
    ├── 08_RAG策略评估与优化方案.md
    └── 09_部署与测试.md
```

## 验证

每次修改后建议执行：

```bash
python -c "import ast; ast.parse(open('app.py', encoding='utf-8').read()); print('[OK]')"
python scripts/smoke_test.py
python -m compileall app.py utils scripts data
```

## 开发路线

- [x] 十问歌结构化问诊
- [x] 多厂商 AI 辨证引擎
- [x] 规则兜底诊断
- [x] 关键问题追问闭环
- [x] Supabase + JSON 双后端
- [x] 数据分析看板
- [x] 一体化中医知识库
- [x] Supabase 诊断面板
- [ ] 病历导出 PDF / Word
- [ ] ChromaDB 向量检索
- [ ] 移动端细节优化

## 作者

沈建伟

- 厦门大学 邹至庄经济研究院 数量经济学硕士
- 厦门大学 医学院 中医学本科

## 许可证

本项目采用 MIT License，详见 [LICENSE](LICENSE)。
