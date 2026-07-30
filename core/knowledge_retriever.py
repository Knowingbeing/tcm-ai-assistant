"""本地中医知识库检索。

第一版采用关键词、同义词与字段权重检索，可替换为 Embedding 或混合检索实现。
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from core.schemas import KNOWLEDGE_VERSION, clean_text, safe_list
from data.tcm_data import FORMULAS, HERBS, SYNDROMES


TYPE_LABELS = {"syndrome": "证型", "formula": "方剂", "herb": "中药"}

SYNONYMS: Dict[str, List[str]] = {
    "怕冷": ["恶寒", "畏寒", "发冷", "寒战"],
    "发热": ["身热", "高热", "潮热"],
    "出汗": ["汗出", "自汗", "盗汗", "大汗"],
    "无汗": ["汗少", "不汗"],
    "咳嗽": ["咳", "咳喘"],
    "痰": ["痰多", "黄痰", "白痰", "痰湿"],
    "头痛": ["头疼", "头身疼痛"],
    "失眠": ["不寐", "多梦"],
    "腹泻": ["便溏", "泄泻", "大便稀"],
    "便秘": ["大便干结", "大便秘结"],
    "口渴": ["口干", "咽干"],
    "胸闷": ["胸胁胀满", "胸胁苦满"],
    "乏力": ["疲乏", "神疲", "气短"],
    "舌红": ["舌质红", "红舌"],
    "苔白": ["舌苔薄白", "白苔"],
    "苔黄": ["黄苔", "舌苔黄"],
    "脉浮": ["浮脉"],
    "脉弦": ["弦脉"],
    "脉数": ["数脉"],
}


@dataclass(frozen=True)
class KnowledgeItem:
    id: str
    type: str
    name: str
    indications: str
    syndrome_category: str
    source: str
    body: str
    cautions: str
    content_version: str = KNOWLEDGE_VERSION
    updated_at: str = "2026-07-30"
    enabled: bool = True

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass(frozen=True)
class KnowledgeHit:
    item: KnowledgeItem
    score: float
    matched_terms: List[str]

    def to_dict(self) -> Dict:
        data = self.item.to_dict()
        data.update({"score": round(self.score, 4), "matched_terms": self.matched_terms})
        return data


class KnowledgeRetriever:
    def retrieve(
        self,
        query: str,
        symptoms: Sequence[str] | None = None,
        tongue: str = "",
        pulse: str = "",
        top_k: int = 8,
        type_filter: Optional[Sequence[str]] = None,
    ) -> List[KnowledgeHit]:
        raise NotImplementedError


def build_knowledge_items() -> List[KnowledgeItem]:
    items: List[KnowledgeItem] = []
    for item in SYNDROMES:
        name = clean_text(item.get("name"), 80)
        body = (
            f"证候：{item.get('symptoms', '')}\n"
            f"舌象：{item.get('tongue', '')}\n"
            f"脉象：{item.get('pulse', '')}\n"
            f"治法：{item.get('treatment', '')}\n"
            f"相关方剂：{item.get('formula', '')}"
        )
        items.append(KnowledgeItem(
            id=f"syndrome:{name}",
            type="syndrome",
            name=name,
            indications=clean_text(item.get("symptoms"), 500),
            syndrome_category=clean_text(item.get("category"), 80),
            source="本地证型库",
            body=clean_text(body, 1200),
            cautions="仅作辨证知识参考，需结合望闻问切与专业判断。",
        ))
    for item in FORMULAS:
        name = clean_text(item.get("name"), 80)
        body = (
            f"组成：{item.get('composition', '')}\n"
            f"功效：{item.get('function', '')}\n"
            f"主治：{item.get('indication', '')}\n"
            f"类别：{item.get('category', '')}"
        )
        items.append(KnowledgeItem(
            id=f"formula:{name}",
            type="formula",
            name=name,
            indications=clean_text(item.get("indication"), 500),
            syndrome_category=clean_text(item.get("category"), 80),
            source=clean_text(item.get("source") or "本地方剂库", 80),
            body=clean_text(body, 1200),
            cautions="方剂信息仅作学习参考，不能据此自行服药或替代处方。",
        ))
    for item in HERBS:
        name = clean_text(item.get("name"), 80)
        body = (
            f"性味：{item.get('nature', '')}，{item.get('flavor', '')}\n"
            f"归经：{item.get('meridian', '')}\n"
            f"功效：{item.get('function', '')}\n"
            f"主治：{item.get('indication', '')}\n"
            f"常用量：{item.get('dosage', '')}"
        )
        items.append(KnowledgeItem(
            id=f"herb:{name}",
            type="herb",
            name=name,
            indications=clean_text(item.get("indication"), 500),
            syndrome_category=clean_text(item.get("meridian"), 80),
            source="本地中药库",
            body=clean_text(body, 1200),
            cautions=clean_text(item.get("caution") or "特殊体质、孕期、儿童、老人请咨询专业人士。", 500),
        ))
    return items


class KeywordKnowledgeRetriever(KnowledgeRetriever):
    def __init__(self, items: Optional[List[KnowledgeItem]] = None, synonyms: Optional[Dict[str, List[str]]] = None):
        self.items = items or build_knowledge_items()
        self.synonyms = synonyms or SYNONYMS

    def retrieve(
        self,
        query: str,
        symptoms: Sequence[str] | None = None,
        tongue: str = "",
        pulse: str = "",
        top_k: int = 8,
        type_filter: Optional[Sequence[str]] = None,
    ) -> List[KnowledgeHit]:
        top_k = max(1, min(20, int(top_k or 8)))
        allowed = set(type_filter or TYPE_LABELS.keys())
        query_text = " ".join([query or "", " ".join(symptoms or []), tongue or "", pulse or ""])
        terms = expand_terms(tokenize(query_text), self.synonyms)
        if not terms:
            return []

        hits: List[KnowledgeHit] = []
        for item in self.items:
            if not item.enabled or item.type not in allowed:
                continue
            score, matched = score_item(item, terms)
            if score > 0:
                hits.append(KnowledgeHit(item=item, score=score, matched_terms=matched))
        hits.sort(key=lambda h: (h.score, type_priority(h.item.type), h.item.name), reverse=True)
        return hits[:top_k]


def tokenize(text: str) -> List[str]:
    text = clean_text(text, 2000)
    chunks = re.findall(r"[\u4e00-\u9fff]{1,12}|[A-Za-z0-9_]+", text)
    terms: List[str] = []
    for chunk in chunks:
        if len(chunk) <= 2:
            terms.append(chunk)
        else:
            terms.append(chunk)
            terms.extend(chunk[i:i + 2] for i in range(len(chunk) - 1))
            terms.extend(chunk[i:i + 3] for i in range(len(chunk) - 2))
    return [t for t in dict.fromkeys(terms) if len(t.strip()) >= 1]


def expand_terms(terms: Iterable[str], synonyms: Dict[str, List[str]]) -> List[str]:
    expanded = list(dict.fromkeys(t for t in terms if t))
    for key, values in synonyms.items():
        group = [key] + values
        if any(term in expanded for term in group):
            expanded.extend(v for v in group if v not in expanded)
    return expanded


def score_item(item: KnowledgeItem, terms: Sequence[str]) -> Tuple[float, List[str]]:
    fields = {
        "name": (item.name, 6.0),
        "indications": (item.indications, 4.5),
        "body": (item.body, 2.0),
        "category": (item.syndrome_category, 1.5),
        "cautions": (item.cautions, 0.8),
    }
    score = 0.0
    matched: List[str] = []
    for term in terms:
        if len(term) == 1 and term not in item.name:
            continue
        term_score = 0.0
        for text, weight in fields.values():
            if term and term in text:
                term_score += weight * (1.0 if len(term) >= 2 else 0.45)
        if term_score:
            matched.append(term)
            score += min(term_score, 10.0)
    type_bonus = {"syndrome": 1.15, "formula": 1.0, "herb": 0.72}.get(item.type, 1.0)
    return score * type_bonus, matched[:10]


def type_priority(item_type: str) -> int:
    return {"syndrome": 3, "formula": 2, "herb": 1}.get(item_type, 0)


def format_hits_for_prompt(hits: Sequence[KnowledgeHit], max_chars: int = 5000) -> str:
    lines: List[str] = []
    for idx, hit in enumerate(hits, start=1):
        item = hit.item
        lines.append(
            f"[K{idx}] id={item.id}｜类型={TYPE_LABELS.get(item.type, item.type)}｜名称={item.name}｜来源={item.source}\n"
            f"适用/证候：{item.indications}\n"
            f"正文：{item.body}\n"
            f"禁忌/注意：{item.cautions}"
        )
    text = "\n\n".join(lines)
    return text[:max_chars]


def evaluate_retriever(retriever: KnowledgeRetriever, cases: Sequence[Dict], top_k: int = 5) -> Dict[str, float]:
    total = len(cases)
    if total == 0:
        return {"cases": 0, "recall_at_k": 0.0, "citation_accuracy": 0.0, "avg_relevance": 0.0}
    recall = 0
    relevance_sum = 0.0
    citation_ok = 0
    for case in cases:
        hits = retriever.retrieve(
            case.get("query", ""),
            case.get("symptoms", []),
            case.get("tongue", ""),
            case.get("pulse", ""),
            top_k=top_k,
        )
        hit_ids = {hit.item.id for hit in hits}
        expected = set(case.get("expected_ids", []))
        if expected and hit_ids.intersection(expected):
            recall += 1
        if all(hit.item.id and hit.item.source for hit in hits):
            citation_ok += 1
        relevance_sum += max((hit.score for hit in hits), default=0.0)
    return {
        "cases": total,
        "recall_at_k": round(recall / total, 4),
        "citation_accuracy": round(citation_ok / total, 4),
        "avg_relevance": round(relevance_sum / total, 4),
    }


_DEFAULT_RETRIEVER: KeywordKnowledgeRetriever | None = None


def get_default_retriever() -> KeywordKnowledgeRetriever:
    global _DEFAULT_RETRIEVER
    if _DEFAULT_RETRIEVER is None:
        _DEFAULT_RETRIEVER = KeywordKnowledgeRetriever()
    return _DEFAULT_RETRIEVER

