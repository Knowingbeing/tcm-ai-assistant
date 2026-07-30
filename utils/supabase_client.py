"""
Supabase 客户端封装（云端持久化）
================================

职责：
1. 单例管理：避免每次请求都新建连接
2. 多源凭证：Streamlit secrets > 环境变量 > 本地 .streamlit/secrets.toml
3. 降级策略：未配置时返回 None，调用方走 JSON 兜底
4. 错误隔离：网络/权限错误不污染上层业务逻辑

上层调用示例：
    from utils.supabase_client import get_records, save_record, get_settings, save_settings

    records = get_records()              # 替代 load_records()
    save_record({...})                    # 替代 save_records(records)
    cfg = get_settings()                  # 替代 load_settings()
    save_settings({...})                  # 替代 save_settings({...})
"""

import os
import json as _json
import streamlit as st
from typing import List, Dict, Optional

try:
    from supabase import create_client, Client
    from postgrest.exceptions import APIError
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None
    APIError = Exception

_CLIENT: Optional["Client"] = None


def _get_credentials() -> tuple[Optional[str], Optional[str]]:
    """从多个来源读取 Supabase 凭证，优先级：
    1. st.secrets（Streamlit Cloud 部署）
    2. 环境变量（本地/CI）
    3. 返回 (None, None) 表示未配置
    """
    url, key = None, None
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY")
    except Exception:
        pass

    if not url:
        url = os.environ.get("SUPABASE_URL")
    if not key:
        key = os.environ.get("SUPABASE_KEY")

    return url, key


def get_client() -> Optional["Client"]:
    """获取 Supabase 客户端单例。未配置或库缺失时返回 None。"""
    global _CLIENT
    if not SUPABASE_AVAILABLE:
        return None

    if _CLIENT is not None:
        return _CLIENT

    url, key = _get_credentials()
    if not url or not key:
        return None

    try:
        _CLIENT = create_client(url, key)
        return _CLIENT
    except Exception as e:
        # 不抛异常：让上层走 JSON 兜底
        print(f"[supabase] 初始化失败：{e}")
        return None


def is_configured() -> bool:
    """快速判断是否已配置 Supabase（不实际建连）"""
    url, key = _get_credentials()
    return bool(url and key)


# --------------------------------------------------------------------------
# 业务封装：consultations 表
# --------------------------------------------------------------------------

def get_records() -> List[Dict]:
    """读取所有问诊记录，按时间倒序。失败时返回空列表。

    兼容性处理：优先按 created_at desc 排序；若列不存在则回退 id desc。
    """
    client = get_client()
    if client is None:
        return []
    try:
        resp = (
            client.table("consultations")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        return resp.data or []
    except Exception as e1:
        # 列不存在/语法错误 → 回退到按 id 倒序
        print(f"[supabase] get_records（created_at 排序）失败，尝试 id 排序：{e1}")
        try:
            resp = (
                client.table("consultations")
                .select("*")
                .order("id", desc=True)
                .execute()
            )
            return resp.data or []
        except Exception as e2:
            print(f"[supabase] get_records（id 排序）失败，返回空：{e2}")
            return []


CONSULTATION_ALLOWED_FIELDS = {
    "patient_id", "name", "age", "gender",
    "chief_complaint", "symptoms",
    "tongue_sign", "pulse_sign",
    "syndrome", "syndrome_category",
    "formula", "formula_adjustment",
    "treatment_principle", "analysis",
    "confidence", "source",
    "session_id", "round_index", "messages",
    "structured_symptoms", "followups", "retrieval_ids",
    "prompt_version", "model_name", "structured_result",
    "safety_tags", "handoff_required", "handoff_reason",
    "model_status",
}


def _clean_json_field(val, default):
    if val is None:
        return default
    if isinstance(val, str):
        try:
            return _json.loads(val)
        except Exception:
            return default
    if isinstance(val, (list, dict)):
        try:
            _json.dumps(val, ensure_ascii=False)
            return val
        except Exception:
            return default
    return default


def _normalize_consultation_payload(record: Dict) -> Dict:
    """把问诊记录规整成 Supabase 与 JSON 共享的结构。"""
    payload = {k: v for k, v in record.items() if k in CONSULTATION_ALLOWED_FIELDS}
    payload["symptoms"] = _clean_json_field(payload.get("symptoms"), [])
    for json_key, default in {
        "messages": [],
        "structured_symptoms": {},
        "followups": [],
        "retrieval_ids": [],
        "structured_result": {},
        "safety_tags": [],
    }.items():
        if json_key in payload:
            payload[json_key] = _clean_json_field(payload.get(json_key), default)
    if "confidence" in payload:
        try:
            payload["confidence"] = max(0, min(100, int(payload["confidence"])))
        except Exception:
            payload["confidence"] = 0
    if not payload.get("chief_complaint"):
        payload["chief_complaint"] = "(未填写)"
    return payload


def save_record(record: Dict) -> tuple:
    """插入单条问诊记录。

    返回 ``(success: bool, error_msg: str)``。
    成功时 error_msg 为空字符串；失败时包含具体原因，供 UI 直接展示。
    """
    client = get_client()
    if client is None:
        return (False, "Supabase 未配置或客户端初始化失败（检查 URL / Key）")

    # 数据清洗：确保 JSON 字段可序列化
    import json as _json

    def _clean_json_field(val, default):
        if val is None:
            return default
        if isinstance(val, str):
            try:
                return _json.loads(val)
            except Exception:
                return default
        if isinstance(val, (list, dict)):
            # 确保内部元素可 JSON 序列化
            try:
                _json.dumps(val, ensure_ascii=False)
                return val
            except Exception:
                return default
        return default

    try:
        allowed = {
            "patient_id", "name", "age", "gender",
            "chief_complaint", "symptoms",
            "tongue_sign", "pulse_sign",
            "syndrome", "syndrome_category",
            "formula", "formula_adjustment",
            "treatment_principle", "analysis",
            "confidence", "source",
            "session_id", "round_index", "messages",
            "structured_symptoms", "followups", "retrieval_ids",
            "prompt_version", "model_name", "structured_result",
            "safety_tags", "handoff_required", "handoff_reason",
            "model_status",
        }
        payload = {k: v for k, v in record.items() if k in allowed}
        payload["symptoms"] = _clean_json_field(payload.get("symptoms"), [])
        for json_key, default in {
            "messages": [],
            "structured_symptoms": {},
            "followups": [],
            "retrieval_ids": [],
            "structured_result": {},
            "safety_tags": [],
        }.items():
            if json_key in payload:
                payload[json_key] = _clean_json_field(payload.get(json_key), default)
        # confidence 约束：0-100，越界则截断
        if "confidence" in payload:
            try:
                c = int(payload["confidence"])
                payload["confidence"] = max(0, min(100, c))
            except Exception:
                payload["confidence"] = 0
        # chief_complaint 是 NOT NULL，空值兜底
        if not payload.get("chief_complaint"):
            payload["chief_complaint"] = "(未填写)"

        client.table("consultations").insert(payload).execute()
        return (True, "")
    except Exception as e:
        error_msg = str(e)
        # 如果是因为缺少字段导致的错误，尝试降级保存
        if "column" in error_msg.lower() or "does not exist" in error_msg.lower():
            fallback_allowed = {
                "name", "age", "gender",
                "chief_complaint", "symptoms",
                "tongue_sign", "pulse_sign",
                "syndrome", "syndrome_category",
                "formula", "formula_adjustment",
                "treatment_principle", "analysis",
                "confidence", "source",
            }
            fallback_payload = {k: v for k, v in record.items() if k in fallback_allowed}
            fallback_payload["symptoms"] = _clean_json_field(fallback_payload.get("symptoms"), [])
            if not fallback_payload.get("chief_complaint"):
                fallback_payload["chief_complaint"] = "(未填写)"
            if "confidence" in fallback_payload:
                try:
                    fallback_payload["confidence"] = max(0, min(100, int(fallback_payload["confidence"])))
                except Exception:
                    fallback_payload["confidence"] = 0
            try:
                client.table("consultations").insert(fallback_payload).execute()
                print(f"[supabase] 降级保存成功（缺少 session_id/round_index/messages 字段）")
                return (True, "")
            except Exception as e2:
                detail = _format_supabase_error(e2)
                print(f"[supabase] 降级保存也失败：{detail}")
                return (False, f"降级保存也失败：{detail}")
        detail = _format_supabase_error(e)
        print(f"[supabase] save_record 失败：{detail}")
        return (False, detail)


def _format_supabase_error(e: Exception) -> str:
    """把 Supabase / PostgREST 异常格式化为用户可读的中文提示。"""
    msg = str(e)
    low = msg.lower()
    if "row level security" in low or "rls" in low:
        return "Supabase 行级安全(RLS)阻止了写入 → 请在 Supabase SQL Editor 执行：ALTER TABLE consultations DISABLE ROW LEVEL SECURITY;"
    if "violates not-null constraint" in low:
        col = ""
        if "column" in low:
            col = msg.split("column")[1].split("of")[0].strip() if "column" in low else ""
        return f"NOT NULL 约束失败（字段 {col} 不能为空）→ 原文：{msg[:200]}"
    if "violates check constraint" in low:
        return f"CHECK 约束失败（值不在允许范围内）→ 原文：{msg[:200]}"
    if "does not exist" in low or "column" in low and "relation" not in low:
        return f"表结构不匹配（列不存在）→ 请在 Supabase SQL Editor 执行 supabase/migration_p1_session.sql → 原文：{msg[:200]}"
    if "relation" in low and "does not exist" in low:
        return "consultations 表不存在 → 请在 Supabase SQL Editor 执行 supabase/schema.sql"
    if "invalid api key" in low or "jwt" in low:
        return "Supabase API Key 无效或已过期 → 请检查 .streamlit/secrets.toml 中的 SUPABASE_KEY"
    if "fetch failed" in low or "connection" in low or "timeout" in low:
        return f"网络连接失败 → 检查 SUPABASE_URL 是否正确、网络是否可达 → 原文：{msg[:200]}"
    return msg[:300]


def diagnose_connection() -> dict:
    """诊断 Supabase 连接与表结构，返回结构化报告。供 UI「诊断」按钮调用。"""
    report = {
        "configured": False,
        "client_ok": False,
        "table_exists": False,
        "columns": [],
        "missing_columns": [],
        "rls_disabled": None,
        "test_insert_ok": False,
        "test_insert_error": "",
        "record_count": -1,
        "errors": [],
    }
    url, key = _get_credentials()
    report["configured"] = bool(url and key)
    if not report["configured"]:
        report["errors"].append("未配置 SUPABASE_URL / SUPABASE_KEY（请检查 .streamlit/secrets.toml 或环境变量）")
        return report

    client = get_client()
    if client is None:
        report["errors"].append("Supabase 客户端初始化失败（URL 或 Key 无效）")
        return report
    report["client_ok"] = True

    # 检测表是否存在 + 有哪些列
    expected_cols = {
        "id", "patient_id", "session_id", "round_index",
        "name", "age", "gender", "chief_complaint", "symptoms",
        "tongue_sign", "pulse_sign", "syndrome", "syndrome_category",
        "formula", "formula_adjustment", "treatment_principle", "analysis",
        "confidence", "source", "messages", "created_at",
        "structured_symptoms", "followups", "retrieval_ids",
        "prompt_version", "model_name", "structured_result",
        "safety_tags", "handoff_required", "handoff_reason", "model_status",
    }
    try:
        resp = client.table("consultations").select("*").limit(1).execute()
        report["table_exists"] = True
        if resp.data:
            report["columns"] = list(resp.data[0].keys())
        else:
            # 表存在但为空，尝试用 RPC 获取列信息
            try:
                col_resp = client.rpc("to_jsonb", {}).execute()
            except Exception:
                pass
            report["columns"] = ["(表为空，无法检测列)"]
        report["missing_columns"] = [c for c in expected_cols if c not in report["columns"]] if resp.data else []
    except Exception as e:
        msg = str(e).lower()
        if "does not exist" in msg or "relation" in msg:
            report["errors"].append("consultations 表不存在 → 请执行 supabase/schema.sql")
        elif "row level security" in msg or "rls" in msg:
            report["rls_disabled"] = False
            report["errors"].append("RLS 已启用，anon key 无法读写 → 请执行：ALTER TABLE consultations DISABLE ROW LEVEL SECURITY;")
        else:
            report["errors"].append(f"查询失败：{str(e)[:200]}")
        return report

    # 检测记录数
    try:
        count_resp = client.table("consultations").select("*", count="exact").execute()
        report["record_count"] = count_resp.count if hasattr(count_resp, "count") else len(count_resp.data)
    except Exception:
        pass

    # 测试插入（用一条 source='draft' 的测试记录，随后删除）
    try:
        test_payload = {
            "name": "_诊断测试_",
            "age": 0,
            "gender": "",
            "chief_complaint": "(诊断测试)",
            "symptoms": [],
            "syndrome": "(诊断测试)",
            "confidence": 0,
            "source": "draft",
        }
        insert_resp = client.table("consultations").insert(test_payload).execute()
        report["test_insert_ok"] = True
        # 清理测试数据
        if insert_resp.data and insert_resp.data[0].get("id"):
            client.table("consultations").delete().eq("id", insert_resp.data[0]["id"]).execute()
    except Exception as e:
        detail = _format_supabase_error(e)
        report["test_insert_error"] = detail
        report["errors"].append(f"测试写入失败：{detail}")

    return report


def get_sessions() -> List[Dict]:
    """读取所有问诊会话（按 session_id 聚合的最新一条），按时间倒序。
    用于"问诊历史"列表：每条只返回该 session 最新一轮的概要。

    兼容性：先按 created_at 排序；若列不存在则按 id 排序；
    若 session_id/round_index 列也不存在则按 id 降序作为「单条会话」返回。
    """
    client = get_client()
    if client is None:
        return []
    # 优先尝试带排序的查询
    last_err = None
    for order_col in ("created_at", "id"):
        try:
            resp = (
                client.table("consultations")
                .select("id,session_id,round_index,syndrome,formula,confidence,created_at,chief_complaint,name")
                .order(order_col, desc=True)
                .execute()
            )
            rows = resp.data or []
            # 按 session_id 取 round_index 最大的一条
            seen = {}
            for r in rows:
                sid = r.get("session_id")
                if not sid:
                    continue
                if sid not in seen or (r.get("round_index") or 0) > (seen[sid].get("round_index") or 0):
                    seen[sid] = r
            return list(seen.values())
        except Exception as e:
            last_err = e
            # 如果是「列不存在」类错误，尝试更小的 select 集合 + 下一排序字段
            print(f"[supabase] get_sessions 按 {order_col} 排序失败：{e}")
            continue
    # 最后兜底：只取必要字段、不排序
    try:
        resp = (
            client.table("consultations")
            .select("id,syndrome,formula,confidence,chief_complaint,name")
            .execute()
        )
        rows = resp.data or []
        # 没有 session_id 字段时，把每条都视作一个独立会话
        return rows
    except Exception as e:
        print(f"[supabase] get_sessions 完全失败：{e}")
        return []


def get_session_history(session_id: str) -> List[Dict]:
    """读取某个 session_id 的全部记录（多轮），按 round_index 升序。

    兼容性：若 round_index 列不存在则只按 id 倒序取该 session 的全部记录。
    """
    client = get_client()
    if client is None:
        return []
    try:
        resp = (
            client.table("consultations")
            .select("*")
            .eq("session_id", session_id)
            .order("round_index", desc=False)
            .execute()
        )
        return resp.data or []
    except Exception as e1:
        print(f"[supabase] get_session_history 失败，尝试 id 排序：{e1}")
        try:
            resp = (
                client.table("consultations")
                .select("*")
                .eq("session_id", session_id)
                .order("id", desc=False)
                .execute()
            )
            return resp.data or []
        except Exception as e2:
            print(f"[supabase] get_session_history 第二次也失败：{e2}")
            return []


def clear_records() -> bool:
    """清空所有问诊记录（管理用）"""
    client = get_client()
    if client is None:
        return False
    try:
        client.table("consultations").delete().gt("id", 0).execute()
        return True
    except Exception as e:
        print(f"[supabase] clear_records 失败：{e}")
        return False


# --------------------------------------------------------------------------
# 业务封装：settings 表（单行，id=1）
# --------------------------------------------------------------------------

_DEFAULT_SETTINGS = {
    "api_key": "",
    "provider": "DeepSeek",
    "model": "",
}


def get_settings() -> Dict:
    """读取系统设置。未配置或查询失败时返回默认值。"""
    client = get_client()
    if client is None:
        return dict(_DEFAULT_SETTINGS)
    try:
        resp = client.table("settings").select("*").eq("id", 1).execute()
        if resp.data:
            row = resp.data[0]
            return {
                "api_key": row.get("api_key") or "",
                "provider": row.get("provider") or "DeepSeek",
                "model": row.get("model") or "",
            }
        return dict(_DEFAULT_SETTINGS)
    except Exception as e:
        print(f"[supabase] get_settings 失败：{e}")
        return dict(_DEFAULT_SETTINGS)


def save_settings(settings: Dict) -> bool:
    """保存系统设置（upsert 到 id=1）"""
    client = get_client()
    if client is None:
        return False
    try:
        payload = {
            "id": 1,
            "api_key": settings.get("api_key", ""),
            "provider": settings.get("provider", "DeepSeek"),
            "model": settings.get("model", ""),
        }
        client.table("settings").upsert(payload).execute()
        return True
    except Exception as e:
        print(f"[supabase] save_settings 失败：{e}")
        return False
