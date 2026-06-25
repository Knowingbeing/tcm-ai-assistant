# 中医AI智能问诊助手 - 项目交接文档

## 项目概述

基于 LLM + RAG 架构的中医智能问诊系统，支持六经辨证、脏腑辨证、卫气营血辨证。

## 项目路径

`D:\用户文件勿删\Desktop\中医AI智能问诊助手\`

## 技术栈

- **前端**：Streamlit
- **后端**：Python
- **AI引擎**：OpenAI 兼容 API（支持 7 家厂商）
- **数据存储**：Supabase Postgres（云端持久化）+ JSON 文件（兜底）
- **部署**：Streamlit Cloud

## 核心文件

| 文件 | 说明 |
|------|------|
| `app.py` | 主应用（约 990 行） |
| `utils/llm_engine.py` | AI 辨证引擎 |
| `utils/supabase_client.py` | Supabase 客户端封装 |
| `data/tcm_data.py` | 中医知识库数据 |
| `supabase/schema.sql` | 数据库建表脚本 |
| `scripts/migrate_json_to_supabase.py` | JSON → Supabase 迁移脚本 |
| `scripts/smoke_test.py` | 冒烟测试（无需真实凭证） |
| `streamlit_app.py` | Streamlit Cloud 入口 |
| `.streamlit/config.toml` | Streamlit 配置 |
| `.streamlit/secrets.toml.example` | Supabase 凭证模板 |

## 已实现功能

1. ✅ 智能问诊（症状采集→证型推理→方剂推荐）
2. ✅ 数据分析看板（证型分布、辨证体系、问诊记录）
3. ✅ 中医知识库（65 方剂、45 证型、70 中药）
4. ✅ 中药库（搜索、药性/药味/归经筛选）
5. ✅ 多厂商 API 支持（DeepSeek/OpenAI/MiMo 等）
6. ✅ API 配置持久化（Supabase 单行表）
7. ✅ 产品级 UI 设计（绿色主题、卡片布局）
8. ✅ **云端持久化（Supabase Postgres）**

## 部署步骤（首次配置 Supabase）

### 1. 注册 Supabase 项目
1. 访问 https://supabase.com/dashboard ，用 GitHub 账号登录
2. New Project → 选区域（推荐 Singapore / Tokyo）
3. 设置 Database Password（妥善保存！）
4. 等待项目初始化完成（约 1-2 分钟）

### 2. 执行建表脚本
1. 左侧菜单 → **SQL Editor** → New query
2. 复制 `supabase/schema.sql` 全部内容粘贴进去
3. 点击 **Run**

### 3. 获取 API 凭证
左侧菜单 → **Project Settings** → **API**，复制：
- `Project URL`（形如 `https://xxxxx.supabase.co`）
- `anon public` key

### 4. 配置到 Streamlit Cloud
在 Streamlit Cloud app 页面 → **Settings** → **Secrets**，填入：
```toml
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...."
```

### 5. 推送代码
```bash
git add -A
git commit -m "feat: 接入 Supabase 云端持久化"
git push
```
Streamlit Cloud 自动重新部署。

### 6. （可选）迁移历史数据
如有 `/tmp/tcm_records.json` 或本地 `tcm_records.json`，可执行：
```bash
export SUPABASE_URL=https://xxxxx.supabase.co
export SUPABASE_KEY=eyJ...
python scripts/migrate_json_to_supabase.py
```

### 7. 验证
- 启动 app，在「智能问诊」保存一条记录
- 打开 Supabase Dashboard → Table Editor → `consultations` 表
- 关闭并重启 app，记录仍在 → 升级成功 ✅

## 本地开发

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置凭证（二选一）
# 方式 A：.streamlit/secrets.toml
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# 编辑 secrets.toml 填入真实值
# 方式 B：环境变量
export SUPABASE_URL=https://xxxxx.supabase.co
export SUPABASE_KEY=eyJ...

# 启动
streamlit run app.py

# 跑冒烟测试
python scripts/smoke_test.py
```

## 降级策略

如果未配置 Supabase 凭证：
- `load_records()` 返回空列表（首次启动）
- `load_settings()` 返回默认配置
- 应用顶部会显示「💾 数据存储：本地 JSON」提示
- 「系统设置 → 数据管理」会标注当前模式

## 待优化项（按优先级）

1. **P0 ✅ 已完成**：升级数据存储为 Supabase
2. **P1**：多轮问诊（追问式对话）
3. **P2**：舌象识别（视觉模型）、用户系统（注册登录）

## GitHub 仓库

https://github.com/Knowingbeing/tcm-ai-assistant

## 注意事项

1. Supabase Free Tier 限制：500MB 数据库、2GB 带宽、5 万行读 / 天（个人项目绰绰有余）
2. 未配置 Supabase 时数据存本地 JSON，Streamlit Cloud 重启会丢失
3. 需要配置 API Key 才能使用 AI 诊断功能
4. `supabase` SDK 已加入 `requirements.txt`，部署时自动安装
