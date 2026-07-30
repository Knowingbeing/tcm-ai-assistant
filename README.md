# 中医 AI 智能问诊助手

基于 Python、Streamlit、OpenAI 兼容 SDK、Supabase 与本地 JSON 的中医知识辅助产品。系统用于结构化采集问诊信息、检索本地中医知识、辅助整理辨证思路与风险提示，不替代执业医师，不提供可直接照方服药的处方服务。

## 当前版本

v2.2：十问歌结构化问诊 + 最多两轮受限追问 + RAG 知识检索 + 医疗安全规则 + 结构化输出校验 + Supabase/JSON 双存储。

## 已实现功能

- 结构化问诊：基于十问歌分阶段采集寒热、汗、头身、胸腹、饮食、二便、睡眠、情志、旧病、病因、舌象、脉象等信息。
- 提交前摘要：展示主诉、症状、舌脉、信息完整度与缺失字段。
- 受限追问：根据信息完整度最多追问 2 轮，每轮最多 2 个问题，已填写信息不重复询问。
- 真正 RAG：把方剂、证型和中药整理成统一知识 Schema，按关键词、同义词与字段权重动态检索 Top-K，并把命中内容注入模型上下文。
- 结构化输出：固定 Schema 包含信息完整度、可能证型、辨证体系、分析依据、知识引用、治法知识、风险提示、置信度、人工接管和是否建议立即就医。
- 医疗安全：模型调用前独立识别胸痛、呼吸困难、意识障碍、大量出血、高热不退、孕期高风险、特殊年龄、严重过敏、自伤风险、处方替代请求和信息严重不足。
- 结果页：展示症状摘要、缺失信息、可能证型、引用知识来源、治法知识、风险提示、模型状态、保存和重新问诊入口。
- 知识库运营：按证型、方剂、中药浏览与搜索，统一 Schema 维护视图，重复检测，检索验证和 JSON 导出。
- 数据看板：问诊数量、证型分布、时间趋势、高频症状、低置信度、安全拦截、人工接管、模型失败、知识引用和检索无结果等指标。
- 双存储：Supabase 优先，本地 JSON 兜底，两种存储保持一致的核心记录结构。

## 架构

```text
Streamlit UI
  ├─ 智能问诊
  ├─ 数据分析
  ├─ 知识库
  └─ 系统设置

业务层
  ├─ app.py                         页面与交互流程
  ├─ core/diagnosis_service.py       安全 -> RAG -> 模型/降级编排
  ├─ core/safety.py                  医疗安全规则
  ├─ core/knowledge_retriever.py     统一知识 Schema 与 Top-K 检索
  ├─ core/schemas.py                 结构化输入/输出校验
  └─ utils/llm_engine.py             OpenAI 兼容模型调用与追问规则

数据层
  ├─ data/tcm_data.py                方剂、证型、中药
  ├─ data/ten_asks.py                十问歌字段配置
  ├─ utils/supabase_client.py        Supabase 读写与诊断
  └─ data/*.json                     本地兜底存储
```

## RAG 链路

1. 从 `data/tcm_data.py` 读取方剂、证型和中药。
2. 转换为统一 Schema：`id/type/name/indications/syndrome_category/source/body/cautions/content_version/updated_at/enabled`。
3. 根据主诉、症状、舌象和脉象进行关键词、同义词和字段权重检索。
4. 返回 Top-K `KnowledgeHit`，包含知识 ID、类型、名称、来源、得分和命中词。
5. 将 Top-K 内容注入模型 Prompt。
6. 结果页展示引用知识名称、类型、来源和相关度。
7. 未检索到可靠依据时，明确提示知识不足，不生成确定性结论。

## 本地运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

也可以使用 Streamlit Cloud 入口：

```bash
streamlit run streamlit_app.py
```

## 环境变量

复制 `.streamlit/secrets.toml.example` 为 `.streamlit/secrets.toml`，或在 Streamlit Cloud Secrets 中配置：

```toml
OPENAI_API_KEY = "sk-..."
DEEPSEEK_API_KEY = "sk-..."
SUPABASE_URL = "https://your-project-ref.supabase.co"
SUPABASE_KEY = "your-anon-key"
```

无 API Key 时，系统不会伪造 AI 结果，只显示本地知识辅助和明确的模型状态。

## Supabase 部署

1. 在 Supabase 创建项目。
2. 在 SQL Editor 执行 `supabase/schema.sql`。
3. 如果是从 v2.1 升级，继续执行 `supabase/migration_v22_rag_safety.sql`。
4. 在 Streamlit Secrets 或环境变量中配置 `SUPABASE_URL` 与 `SUPABASE_KEY`。
5. 在应用「系统设置」页点击 Supabase 诊断，确认表、字段和写入权限正常。

## Docker 部署

```bash
docker build -t tcm-ai-assistant .
docker run --rm -p 8501:8501 --env-file .env tcm-ai-assistant
```

`.env` 示例：

```env
OPENAI_API_KEY=
DEEPSEEK_API_KEY=
SUPABASE_URL=
SUPABASE_KEY=
```

## Streamlit Cloud 部署

1. 将仓库推送到 GitHub。
2. 在 Streamlit Cloud 新建应用，入口文件选择 `streamlit_app.py`。
3. 在 Secrets 中粘贴 `.streamlit/secrets.toml.example` 对应字段。
4. 部署后先打开「系统设置」页做 Supabase 诊断。

## 验证

```bash
python -c "import ast; ast.parse(open('app.py', encoding='utf-8').read()); print('[OK]')"
python scripts/smoke_test.py
python -m compileall app.py utils scripts data core
```

`scripts/smoke_test.py` 覆盖 15 类核心验收：十问歌、追问、RAG、Prompt 注入、引用一致性、结构化输出、模型失败、安全拦截、低置信度拒答、存储结构、历史会话、看板指标、密钥/隐私、无 Key 测试与检索评测。

## 演示病例

演示病例位于 `core/demo_cases.py`：

- 信息较完整低风险病例：恶寒、无汗、头痛、舌苔薄白、脉浮紧。
- 信息不足病例：咳嗽一周、痰多、缺舌脉，需要追问。
- 急症拦截病例：突发胸痛伴呼吸困难，应中断普通问诊并建议及时就医。

## 后续边界

- 当前 RAG v1 是关键词/同义词/字段权重检索，尚未接入 Embedding 或 ChromaDB。
- 知识库运营页已支持浏览、检索、查重和导出，正式开放新增/编辑前还需要角色权限、审核流和版本记录。
- 模型调用依赖用户配置的 OpenAI 兼容服务，真实线上稳定性需要结合厂商限流、超时和可用性继续观测。
- 产品仅用于知识辅助和信息结构化，不适用于急危重症处理或替代线下诊疗。
