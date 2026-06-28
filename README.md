# 🏥 中医AI智能问诊助手

基于 LLM 的中医智能问诊系统，结合**十问歌结构化表单**与经典中医知识库，实现"症状采集 → AI 辨证 → 方剂推荐"的完整问诊流程。

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?logo=supabase)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ 功能特性

### 📋 智能问诊（十问歌结构化表单）
- 中医十问歌分项填写（寒热、出汗、睡眠、饮食、大小便等）
- 主诉 + 伴随症状多选 + 舌象/脉象选择
- 点击"开始问诊"直接调用 AI 辨证，无需多轮对话
- 支持手动补充症状描述

### 📊 数据分析看板
- 问诊量趋势分析（按日/周/月）
- 证型分布统计（饼图 + 柱状图）
- 症状频率分析
- 方剂使用统计
- 存储后端状态显示（Supabase 云端 / JSON 本地）

### 📚 中医知识库
- **方剂库**：60+ 经方时方，按类别筛选，支持搜索
- **证型库**：50+ 证型，涵盖六经/脏腑/气血津液/卫气营血辨证
- **中药库**：50+ 中药，支持按药性/药味/归经查询
- 知识库规模持续扩充中

### ⚙️ 系统设置
- 支持 7 家 AI 厂商（DeepSeek 推荐，价格实惠效果好）
- Supabase 云端存储配置（URL + Anon Key）
- API Key 状态实时同步显示
- 诊断记录本地 / 云端管理

## 🛠️ 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit 前端                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ 智能问诊  │ │ 数据分析  │ │ 知识库   │ │ 系统设置  │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Python 后端逻辑                           │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │   LLM 辨证引擎    │  │   数据分析模块    │                │
│  │ (7家厂商支持)     │  │   (Pandas)       │                │
│  └──────────────────┘  └──────────────────┘                │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  十问歌数据模块   │  │   Supabase 客户端 │                │
│  │  (data/ten_asks) │  │  (utils/)         │                │
│  └──────────────────┘  └──────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    双存储后端                               │
│  ┌────────────────────┐    ┌──────────────────────────┐    │
│  │  Supabase（优先）   │    │  JSON 文件（兜底）      │    │
│  │  consultations 表   │    │  data/tcm_records.json  │    │
│  │  patients / settings│    │  data/tcm_settings.json │    │
│  └────────────────────┘    └──────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 快速开始

### 本地运行

```bash
# 克隆项目
git clone https://github.com/shenjianwei/tcm-ai-assistant.git
cd tcm-ai-assistant

# 安装依赖
pip install -r requirements.txt

# 配置 API Key（推荐 DeepSeek，也可使用 OpenAI / 通义千问 / 文心一言等）
# 方式一：在应用「系统设置」Tab 中直接填写（推荐）
# 方式二：创建 .streamlit/secrets.toml
# DEEPSEEK_API_KEY = "sk-xxx"

# （可选）配置 Supabase 云端存储
# 在 .streamlit/secrets.toml 中添加：
# SUPABASE_URL = "https://xxx.supabase.co"
# SUPABASE_KEY = "eyJhbG..."

# 启动应用
streamlit run app.py
```

### Streamlit Cloud 部署（推荐）

1. Fork 本项目到你的 GitHub
2. 在 [Streamlit Cloud](https://streamlit.io/cloud) 中关联仓库
3. 在 `Advanced Settings` → `Secrets` 中填入：
   ```toml
   DEEPSEEK_API_KEY = "sk-xxx"
   SUPABASE_URL = "https://xxx.supabase.co"
   SUPABASE_KEY = "eyJhbG..."
   ```
4. 点击 Deploy，等待部署完成

## 📁 项目结构

```
中医AI智能问诊助手/
├── app.py                    # Streamlit 主应用（1959 行）
├── requirements.txt          # Python 依赖
├── README.md                # 项目说明（本文件）
├── LICENSE                  # MIT 许可证
├── .gitignore               # Git 忽略配置
├── .streamlit/
│   └── secrets.toml.example  # Streamlit secrets 模板
├── data/
│   ├── tcm_data.py         # 方剂/证型/中药知识库（60+ 方剂, 50+ 证型, 50+ 中药）
│   └── ten_asks.py        # 十问歌结构化数据定义
├── utils/
│   ├── llm_engine.py       # AI 辨证引擎（支持 7 家厂商）
│   └── supabase_client.py  # Supabase 客户端封装（云端持久化）
├── supabase/
│   ├── schema.sql          # Supabase 表结构（consultations / patients / settings）
│   └── migration_p1_session.sql  # 多轮会话字段迁移脚本
└── data/                   # 本地 JSON 存储目录（兜底）
    ├── tcm_records.json    # 问诊记录
    └── tcm_settings.json   # 用户配置
```

## 🔧 配置说明

### AI 引擎（支持 7 家厂商）

| 厂商 | 模型示例 | API Key 前缀 | 推荐度 |
|------|---------|-------------|--------|
| DeepSeek | deepseek-chat | sk- | ⭐⭐⭐⭐⭐ 推荐 |
| OpenAI | gpt-3.5-turbo | sk- | ⭐⭐⭐⭐ |
| 通义千问 | qwen-turbo | sk- | ⭐⭐⭐ |
| 文心一言 | ERNIE-Bot-4 | 无 | ⭐⭐⭐ |
| 讯飞星火 | generalv3.5 | 无 | ⭐⭐⭐ |
| 智谱 GLM | glm-4-flash | 无 | ⭐⭐⭐ |
| Moonshot | moonshot-v1-8k | sk- | ⭐⭐⭐ |

**获取 API Key 后，在应用「系统设置」Tab 中填入即可，无需重启。**

### Supabase 云端存储（可选）

1. 在 [Supabase](https://supabase.com) 创建项目
2. 在 SQL Editor 中执行 `supabase/schema.sql` 创建表
3. 如需多轮会话功能，再执行 `supabase/migration_p1_session.sql`
4. 在 `.streamlit/secrets.toml` 中填入 URL 和 Key：
   ```toml
   SUPABASE_URL = "https://your-project.supabase.co"
   SUPABASE_KEY = "your-anon-key"
   ```
5. 如遇到 RLS 拦截写入，在 SQL Editor 中执行：
   ```sql
   ALTER TABLE consultations DISABLE ROW LEVEL SECURITY;
   ALTER TABLE patients DISABLE ROW LEVEL SECURITY;
   ALTER TABLE settings DISABLE ROW LEVEL SECURITY;
   ```

## 📊 知识库规模

| 类别 | 数量 | 说明 |
|------|------|------|
| 证型 | 50+ | 六经/脏腑/气血津液/卫气营血/三焦辨证 |
| 方剂 | 60+ | 经方+时方，按类别分类 |
| 症状 | 150+ | 含舌诊脉诊细分 |
| 中药 | 50+ | 性味归经、功效主治 |

## 🎯 开发计划

- [x] 十问歌结构化问诊表单
- [x] AI 辨证引擎（7 家厂商支持）
- [x] Supabase 云端持久化 + JSON 本地兜底
- [x] 数据分析看板（趋势/分布/频率）
- [x] 中医知识库（方剂/证型/中药）
- [x] API Key 四路判定 + 状态实时同步
- [x] 保存失败错误透传 + Supabase 诊断面板
- [ ] 多轮深度问诊（根据辨证结果追问）
- [ ] ChromaDB 向量检索（证型/方剂语义搜索）
- [ ] 病历导出（PDF / Word）
- [ ] 移动端适配

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 👨‍💻 作者

**沈建伟**
- 厦门大学 邹至庄经济研究院 数量经济学硕士
- 厦门大学 医学院 中医学本科
- Email: 2289357543@qq.com

## 🙏 致谢

- 《伤寒论》- 张仲景
- 《温病条辨》- 吴鞠通
- 《中医诊断学》- 全国高等中医药院校教材
- Streamlit - 优秀的 Python Web 框架
- Supabase - 开源的 Firebase 替代品
- DeepSeek - 高性价比的 AI 大模型 API
