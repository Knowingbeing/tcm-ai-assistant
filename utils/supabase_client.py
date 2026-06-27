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


def save_record(record: Dict) -> bool:
    """插入单条问诊记录。返回是否成功。"""
    client = get_client()
    if client is None:
        return False
    try:
        # 仅保留数据库已知列，避免脏字段写入失败
        allowed = {
            "patient_id", "name", "age", "gender",
            "chief_complaint", "symptoms",
            "tongue_sign", "pulse_sign",
            "syndrome", "syndrome_category",
            "formula", "formula_adjustment",
            "treatment_principle", "analysis",
            "confidence", "source",
            "session_id", "round_index", "messages",
        }
        payload = {k: v for k, v in record.items() if k in allowed}
        # symptoms 需为 list 类型
        if isinstance(payload.get("symptoms"), str):
            import json
            try:
                payload["symptoms"] = json.loads(payload["symptoms"])
            except Exception:
                payload["symptoms"] = []
        # messages 同理
        if isinstance(payload.get("messages"), str):
            import json
            try:
                payload["messages"] = json.loads(payload["messages"])
            except Exception:
                payload["messages"] = []
        # 确保 messages 是 JSON 格式
        if "messages" in payload and not isinstance(payload["messages"], (list, dict)):
            payload["messages"] = []
        client.table("consultations").insert(payload).execute()
        return True
    except Exception as e:
        # 如果是因为缺少字段导致的错误，尝试降级保存
        error_msg = str(e)
        if "column" in error_msg.lower() or "does not exist" in error_msg.lower():
            # 移除可能导致问题的字段，重试
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
            if isinstance(fallback_payload.get("symptoms"), str):
                import json
                try:
                    fallback_payload["symptoms"] = json.loads(fallback_payload["symptoms"])
                except Exception:
                    fallback_payload["symptoms"] = []
            try:
                client.table("consultations").insert(fallback_payload).execute()
                print(f"[supabase] 降级保存成功（缺少部分字段）")
                return True
            except Exception as e2:
                print(f"[supabase] 降级保存也失败：{e2}")
                return False
        print(f"[supabase] save_record 失败：{e}")
        return False


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
