# LLM+RAG 策略评估与优化方案

## 1. 当前策略分析

### 1.1 现状：伪 RAG（静态 Prompt 注入）

当前 `llm_engine.py` 中的 `_load_knowledge_base()` 方法返回一段**硬编码的中医理论大纲字符串**，直接拼接到每次 LLM 调用的 system prompt 中。

```python
def _load_knowledge_base(self) -> str:
    return """中医辨证体系参考：
    一、六经辨证（伤寒论）...
    二、脏腑辨证...
    三、卫气营血辨证...
    四、气血津液辨证...
    五、八纲辨证...
    """
```

**这不是真正的 RAG**，而是静态 prompt 注入。`data/tcm_data.py` 中的 68 首方剂、47 个证型、87 味中药**完全没有被 AI 引擎使用**，仅在知识库 Tab 中展示。

### 1.2 当前方案的问题

| 问题 | 影响 | 严重程度 |
|------|------|----------|
| 知识源未利用 | tcm_data.py 中 200+ 条结构化数据未参与辨证 | 🔴 高 |
| 静态注入 | 每次调用都携带相同的知识库文本，不根据症状动态检索 | 🟡 中 |
| Token 浪费 | 硬编码字符串约 500 token，但内容粗略，信息密度低 | 🟡 中 |
| 方剂推荐不准 | LLM 不知道具体方剂组成和主治，推荐可能脱离项目知识库 | 🔴 高 |
| 中药信息缺失 | LLM 无法参考中药性味归经、用量禁忌 | 🟡 中 |
| 无法增量更新 | 知识更新需修改代码，非开发者无法维护 | 🟡 中 |

### 1.3 当前方案的优势（不应丢弃的部分）

- **规则引擎兜底**：20+ 证型的关键词匹配，保证无 API Key 时仍可用
- **多服务商支持**：7 家厂商统一接入，灵活性高
- **多轮追问机制**：结构化信息采集，弥补 LLM 单次输入不足
- **JSON 结构化输出**：辨证结果可解析、可存储

## 2. 真正的 RAG 实现方案

### 2.1 方案对比

| 方案 | 技术栈 | 复杂度 | 效果 | 适用场景 |
|------|--------|--------|------|----------|
| A. 全量注入 | 无需额外组件 | 最低 | 中等 | 知识量 < 2000 token |
| B. 关键词检索 + 注入 | 纯 Python | 低 | 良好 | 知识量 < 50KB |
| C. 向量检索 RAG | embedding + 向量数据库 | 中 | 优秀 | 知识量 > 50KB |
| D. 混合检索 RAG | 向量 + 关键词 + 重排序 | 高 | 最优 | 生产级应用 |

### 2.2 推荐方案：B（关键词检索 + 注入）→ 逐步升级到 C

**理由**：
1. 当前知识库总量约 30KB（tcm_data.py），方案 A 的全量注入已可行但 token 效率低
2. 方案 B 用纯 Python 实现，无需额外依赖，适合当前项目规模
3. 方案 C 需要引入 embedding 模型和向量存储，增加部署复杂度，但效果最优
4. 建议先实施 B 验证效果，再按需升级到 C

### 2.3 方案 B 详细设计：症状驱动的知识检索

#### 2.3.1 架构

```
用户输入（主诉 + 症状 + 舌象 + 脉象）
          │
          ▼
    ┌─────────────────┐
    │  知识检索器       │
    │  (KnowledgeRetriever) │
    └──────┬──────────┘
           │
    ┌──────▼──────────────────────────┐
    │                                   │
    │  1. 证型匹配                       │
    │     从 SYNDROMES 中按症状关键词     │
    │     匹配 Top-5 相关证型             │
    │                                   │
    │  2. 方剂匹配                       │
    │     从 FORMULAS 中按主治关键词      │
    │     匹配 Top-5 相关方剂             │
    │                                   │
    │  3. 中药匹配                       │
    │     从 HERBS 中按功效/主治关键词    │
    │     匹配 Top-5 相关中药             │
    │                                   │
    └──────┬──────────────────────────┘
           │
           ▼
    ┌─────────────────┐
    │  Prompt 构造器    │
    │  将检索结果格式化  │
    │  注入 system prompt│
    └──────┬──────────┘
           │
           ▼
    ┌─────────────────┐
    │  LLM 调用        │
    │  (OpenAI SDK)   │
    └─────────────────┘
```

#### 2.3.2 检索器实现

```python
# utils/knowledge_retriever.py (新增文件)

from data.tcm_data import FORMULAS, SYNDROMES, HERBS

class KnowledgeRetriever:
    """中医知识库检索器"""
    
    def __init__(self):
        self.formulas = FORMULAS
        self.syndromes = SYNDROMES
        self.herbs = HERBS
    
    def retrieve(self, chief_complaint: str, symptoms: list[str],
                 tongue_sign: str, pulse_sign: str) -> str:
        """
        根据患者信息检索相关知识，返回格式化的知识文本。
        
        检索策略：
        1. 证型匹配：症状关键词 + 舌象 + 脉象
        2. 方剂匹配：证型对应方剂 + 主治关键词
        3. 中药匹配：方剂组成中的中药
        """
        text = f"{chief_complaint} {' '.join(symptoms)} {tongue_sign} {pulse_sign}"
        
        # 1. 证型匹配
        matched_syndromes = self._match_syndromes(text, tongue_sign, pulse_sign)
        
        # 2. 方剂匹配
        matched_formulas = self._match_formulas(text, matched_syndromes)
        
        # 3. 中药匹配
        matched_herbs = self._match_herbs(matched_formulas)
        
        # 格式化输出
        return self._format_knowledge(
            matched_syndromes, matched_formulas, matched_herbs
        )
    
    def _match_syndromes(self, text: str, 
                         tongue: str, pulse: str) -> list[dict]:
        """匹配证型，返回 Top-5"""
        scored = []
        for syn in self.syndromes:
            score = 0
            # 症状关键词匹配
            for kw in syn["symptoms"].split("、"):
                if kw in text:
                    score += 2
            # 舌象匹配
            if syn["tongue"] and syn["tongue"] in tongue:
                score += 3
            # 脉象匹配
            if syn["pulse"] and syn["pulse"] in pulse:
                score += 3
            if score > 0:
                scored.append((score, syn))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [s[1] for s in scored[:5]]
    
    def _match_formulas(self, text: str, 
                        syndromes: list[dict]) -> list[dict]:
        """匹配方剂，返回 Top-5"""
        # 从匹配的证型中提取推荐方剂
        formula_names = {s["formula"] for s in syndromes}
        
        scored = []
        for formula in self.formulas:
            score = 0
            # 证型推荐方剂直接加分
            if formula["name"] in formula_names:
                score += 5
            # 主治关键词匹配
            for kw in formula["indication"].split("、"):
                if kw in text:
                    score += 2
            # 功效关键词匹配
            for kw in formula["function"].split("、"):
                if kw in text:
                    score += 1
            if score > 0:
                scored.append((score, formula))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [s[1] for s in scored[:5]]
    
    def _match_herbs(self, formulas: list[dict]) -> list[dict]:
        """匹配中药，返回方剂组成中的中药信息"""
        herb_names = set()
        for f in formulas:
            # 解析方剂组成中的药名
            for name in f["composition"].replace("、", ",").split(","):
                name = name.strip()
                if name:
                    herb_names.add(name)
        
        # 从 HERBS 中查找详细信息
        matched = []
        for herb in self.herbs:
            if herb["name"] in herb_names:
                matched.append(herb)
        
        return matched[:10]  # 最多 10 味
    
    def _format_knowledge(self, syndromes: list[dict],
                          formulas: list[dict],
                          herbs: list[dict]) -> str:
        """格式化检索结果为 prompt 文本"""
        lines = ["根据患者症状，检索到以下相关知识供参考：\n"]
        
        if syndromes:
            lines.append("【相关证型】")
            for s in syndromes:
                lines.append(
                    f"- {s['name']}（{s['category']}）："
                    f"症状={s['symptoms']}，舌={s['tongue']}，"
                    f"脉={s['pulse']}，推荐方剂={s['formula']}，"
                    f"治法={s['treatment']}"
                )
            lines.append("")
        
        if formulas:
            lines.append("【相关方剂】")
            for f in formulas:
                lines.append(
                    f"- {f['name']}（{f['category']}）："
                    f"组成={f['composition']}，功效={f['function']}，"
                    f"主治={f['indication']}，来源={f['source']}"
                )
            lines.append("")
        
        if herbs:
            lines.append("【相关中药】")
            for h in herbs:
                lines.append(
                    f"- {h['name']}：性={h['nature']}，味={h['flavor']}，"
                    f"归经={h['meridian']}，功效={h['function']}，"
                    f"用量={h['dosage']}，禁忌={h['caution']}"
                )
            lines.append("")
        
        lines.append("请结合以上知识和患者具体症状进行辨证分析。")
        return "\n".join(lines)
```

#### 2.3.3 引擎集成

```python
# llm_engine.py 修改

class TCMDiagnosisEngine:
    def __init__(self, api_key, provider="DeepSeek", model=""):
        # ... 原有初始化 ...
        
        # 替换 _load_knowledge_base() 
        # 旧：self.knowledge_base = self._load_knowledge_base()
        # 新：
        from utils.knowledge_retriever import KnowledgeRetriever
        self.retriever = KnowledgeRetriever()
    
    def analyze_symptoms(self, chief_complaint, symptoms, 
                         tongue_sign, pulse_sign):
        # ... 原有逻辑 ...
        
        # 动态检索相关知识
        retrieved_knowledge = self.retriever.retrieve(
            chief_complaint, symptoms, tongue_sign, pulse_sign
        )
        
        system_prompt = f"""你是一位经验丰富的中医师，擅长辨证论治。

{retrieved_knowledge}

请根据患者信息进行辨证分析，返回 JSON 格式结果：
{{
    "syndrome": "证型名称",
    "syndrome_category": "辨证体系",
    "analysis": "详细辨证分析，结合检索到的知识",
    "formula": "推荐方剂（优先从相关方剂中选择）",
    "formula_adjustment": "加减建议",
    "treatment_principle": "治法",
    "confidence": 0-100整数
}}"""
        # ... 后续 LLM 调用逻辑不变 ...
```

#### 2.3.4 效果预估

| 指标 | 当前（静态注入） | 方案 B（关键词检索） | 提升 |
|------|-----------------|---------------------|------|
| 知识利用率 | ~10%（仅大纲） | ~80%（Top-5 检索） | +70% |
| Token 消耗 | ~500 token/次 | ~300-800 token/次（动态） | 相当 |
| 方剂推荐准确率 | 依赖 LLM 内部知识 | 基于知识库匹配 | 显著提升 |
| 中药信息完整度 | 无 | 包含性味归经用量禁忌 | 从无到有 |
| 实现复杂度 | - | 低（纯 Python） | - |
| 额外依赖 | 无 | 无 | - |

### 2.4 方案 C 展望：向量检索 RAG（未来升级路径）

当知识库扩展到更大规模（如加入《伤寒论》全文、《本草纲目》条目等）时，关键词检索的召回率会下降，此时应升级到向量检索。

#### 2.4.1 架构

```
知识库数据 (tcm_data.py + 未来扩展)
          │
          ▼
    ┌──────────────┐
    │ 文档分块器     │  将每条方剂/证型/中药转为一个文档块
    └──────┬───────┘
           │
    ┌──────▼───────┐
    │ Embedding    │  使用 text-embedding 模型生成向量
    │ 模型          │  (如 text-embedding-3-small)
    └──────┬───────┘
           │
    ┌──────▼───────┐
    │ 向量存储      │  Supabase pgvector 扩展
    │ (pgvector)   │  或 ChromaDB (本地)
    └──────┬───────┘
           │
    ┌──────▼───────┐
    │ 检索时        │  用户症状 → embedding → 向量相似度搜索
    │ Top-K 检索   │  → 返回最相关的知识块
    └──────────────┘
```

#### 2.4.2 Supabase pgvector 方案

```sql
-- 启用 pgvector 扩展
create extension if not exists vector;

-- 创建知识库向量表
create table if not exists knowledge_embeddings (
    id          bigserial primary key,
    doc_type    text not null,          -- 'formula' / 'syndrome' / 'herb'
    doc_id      text not null,           -- 文档标识（方剂名/证型名/药名）
    content     text not null,           -- 原始文本
    embedding   vector(1536),            -- 向量（维度取决于 embedding 模型）
    metadata    jsonb default '{}'::jsonb  -- 附加元数据
);

-- 向量相似度索引
create index if not exists idx_knowledge_embedding 
    on knowledge_embeddings using ivfflat (embedding vector_cosine_ops);
```

#### 2.4.3 升级路径

```
当前状态                    方案 B                      方案 C
(静态注入)              (关键词检索)               (向量检索 RAG)
    │                       │                          │
    │  ←── 立即实施 ──────  │  ←── 知识库扩大后 ──────  │
    │                       │                          │
    ▼                       ▼                          ▼
_load_knowledge_base()   KnowledgeRetriever      向量检索 + pgvector
(硬编码字符串)           (纯 Python 关键词匹配)   (embedding + 相似度搜索)
```

## 3. 补充优化建议

### 3.1 Function Calling / Structured Output

当前依赖 LLM 返回 JSON 字符串再解析，存在格式不规范风险。可升级为 Function Calling：

```python
# 使用 OpenAI 的 response_format 参数
resp = self.client.chat.completions.create(
    model=self.model,
    messages=messages,
    temperature=0.3,
    response_format={"type": "json_object"},  # 强制 JSON 输出
    # 或使用 function calling
    functions=[{
        "name": "diagnose",
        "description": "中医辨证诊断",
        "parameters": {
            "type": "object",
            "properties": {
                "syndrome": {"type": "string"},
                "syndrome_category": {"type": "string"},
                "analysis": {"type": "string"},
                "formula": {"type": "string"},
                "formula_adjustment": {"type": "string"},
                "treatment_principle": {"type": "string"},
                "confidence": {"type": "integer", "minimum": 0, "maximum": 100}
            },
            "required": ["syndrome", "analysis", "formula", "confidence"]
        }
    }],
    function_call={"name": "diagnose"}
)
```

**注意**：需要验证各服务商对 `response_format` 和 `function_calling` 的支持情况。DeepSeek 支持 Function Calling。

### 3.2 缓存检索结果

```python
from functools import lru_cache

class KnowledgeRetriever:
    @lru_cache(maxsize=128)
    def retrieve_cached(self, symptoms_hash: str, ...) -> str:
        """缓存检索结果，避免相同症状重复检索"""
        return self.retrieve(...)
```

### 3.3 知识库可扩展性

将知识库从 Python 常量迁移到 Supabase 数据库表，支持非开发者维护：

```sql
-- 未来的知识库表设计
create table tcm_formulas (
    id          bigserial primary key,
    name        text not null unique,
    composition text,
    function    text,
    indication  text,
    source      text,
    category    text,
    embedding   vector(1536)  -- 预留向量字段
);

create table tcm_syndromes (
    id          bigserial primary key,
    name        text not null unique,
    category    text,
    symptoms    text,
    tongue      text,
    pulse       text,
    formula     text,
    treatment   text,
    embedding   vector(1536)
);
```

### 3.4 辨证质量评估

引入辨证结果的自动评估机制：

```python
def evaluate_diagnosis(result: dict, patient_info: dict) -> dict:
    """
    评估辨证结果质量
    
    检查项：
    1. 证型是否在 SYNDROMES 列表中（或足够接近）
    2. 方剂是否在 FORMULAS 列表中
    3. 置信度是否合理
    4. 分析文本长度是否达标
    """
    # ...
```

## 4. 实施优先级

| 优先级 | 任务 | 工作量 | 预期效果 |
|--------|------|--------|----------|
| P0 | 实施 KnowledgeRetriever（方案 B） | 1-2 小时 | 知识利用率从 10% → 80% |
| P1 | 集成到 analyze_symptoms / diagnose_with_conversation | 30 分钟 | 辨证准确率提升 |
| P1 | 升级 JSON 输出为 response_format | 30 分钟 | 减少 JSON 解析失败 |
| P2 | 检索结果缓存 | 30 分钟 | 减少重复计算 |
| P3 | 知识库迁移到数据库表 | 2-3 小时 | 支持非开发者维护 |
| P4 | 向量检索 RAG（方案 C） | 4-6 小时 | 支持大规模知识库 |
| P4 | 辨证质量自动评估 | 1-2 小时 | 质量监控 |

## 5. 总结与建议

**推荐立即实施方案 B（关键词检索 + 注入）**，理由：

1. **零额外依赖**：纯 Python 实现，不需要 embedding 模型或向量数据库
2. **立竿见影**：将 tcm_data.py 中 200+ 条结构化数据纳入 AI 辨证流程
3. **向后兼容**：未来升级到方案 C 时，KnowledgeRetriever 的接口不变，只需替换内部实现
4. **风险可控**：即使检索结果不理想，LLM 仍可依赖自身知识进行辨证，不会比现状更差

**保留 LLM+RAG 策略**的决策是正确的。RAG 的核心价值在于将领域知识注入通用 LLM，而非依赖 LLM 的参数化记忆。对于中医这种专业性强的领域，RAG 是必要的技术选择。当前的问题是"伪 RAG"（静态注入），升级为真正的动态检索后，辨证质量将显著提升。
