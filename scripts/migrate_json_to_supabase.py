"""
JSON → Supabase 数据迁移脚本
============================

适用场景：
  本地或 Streamlit Cloud 历史 JSON 数据，需要迁移到新的 Supabase 后端。

用法：
  1. 在项目根目录放置 tcm_records.json 和 tcm_settings.json
     （可从 /tmp 目录、Streamlit Cloud 备份、或本地 data 目录复制）
  2. 配置 SUPABASE_URL / SUPABASE_KEY（环境变量或 .streamlit/secrets.toml）
  3. 运行：python scripts/migrate_json_to_supabase.py

幂等性：
  - consultations 表按 chief_complaint + created_at 去重
  - settings 表 upsert 到 id=1

安全：
  - 不会清空目标表，只追加
  - 写入失败时打印错误并继续
"""

import os
import sys
import json
from datetime import datetime

# 把项目根目录加入 sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from utils.supabase_client import (
    get_client, get_records, save_record, save_settings, is_configured,
)


def load_json_records(path: str) -> list:
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception as e:
        print(f"[!] 读取 {path} 失败：{e}")
        return []


def load_json_settings(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[!] 读取 {path} 失败：{e}")
        return {}


def find_json_files() -> tuple:
    """按优先级查找 JSON 数据文件"""
    candidates = [
        ("/tmp/tcm_records.json", "/tmp/tcm_settings.json"),
        (os.path.join(PROJECT_ROOT, "tcm_records.json"),
         os.path.join(PROJECT_ROOT, "tcm_settings.json")),
        (os.path.join(PROJECT_ROOT, "data", "tcm_records.json"),
         os.path.join(PROJECT_ROOT, "data", "tcm_settings.json")),
    ]
    for r, s in candidates:
        if os.path.exists(r) or os.path.exists(s):
            return r, s
    return candidates[1]  # 默认返回根目录路径（不存在也不报错）


def main():
    print("=" * 60)
    print("中医AI智能问诊助手 — JSON → Supabase 数据迁移")
    print("=" * 60)

    if not is_configured():
        print("\n[✗] 未检测到 Supabase 配置。请先设置环境变量：")
        print("    export SUPABASE_URL=https://xxxxx.supabase.co")
        print("    export SUPABASE_KEY=eyJhbGciOi...\n")
        sys.exit(1)

    client = get_client()
    if client is None:
        print("[✗] Supabase 客户端初始化失败")
        sys.exit(1)
    print("[✓] Supabase 客户端已连接")

    records_path, settings_path = find_json_files()
    print(f"[*] 扫描数据文件：")
    print(f"    records : {records_path}")
    print(f"    settings: {settings_path}")

    # 1. 迁移问诊记录
    records = load_json_records(records_path)
    print(f"\n[*] 找到 {len(records)} 条问诊记录")

    if records:
        # 读取已存在的云端记录，用于去重
        existing = get_records()
        existing_keys = {
            (r.get("chief_complaint", ""), r.get("date", "")[:19])
            for r in existing
        }

        success, skipped, failed = 0, 0, 0
        for r in records:
            # 兼容旧 JSON 中的 id/date 字段名
            chief = r.get("chief_complaint", "")
            date = r.get("date", "")[:19]
            key = (chief, date)
            if key in existing_keys and chief and date:
                skipped += 1
                continue

            # 映射到 Supabase 字段
            payload = {
                "name": r.get("name", "匿名"),
                "age": r.get("age", 0),
                "gender": r.get("gender", ""),
                "chief_complaint": chief,
                "symptoms": r.get("symptoms", []) or [],
                "tongue_sign": r.get("tongue_sign", ""),
                "pulse_sign": r.get("pulse_sign", ""),
                "syndrome": r.get("syndrome", "待辨证"),
                "syndrome_category": r.get("syndrome_category", ""),
                "formula": r.get("formula", "待推荐"),
                "formula_adjustment": r.get("formula_adjustment", ""),
                "treatment_principle": r.get("treatment_principle", ""),
                "analysis": r.get("analysis", ""),
                "confidence": r.get("confidence", 0),
                "source": "imported",
            }
            if save_record(payload):
                success += 1
            else:
                failed += 1

        print(f"    成功：{success}  跳过：{skipped}  失败：{failed}")

    # 2. 迁移系统设置
    settings = load_json_settings(settings_path)
    if settings and any(settings.values()):
        print(f"\n[*] 导入系统设置：{settings.get('provider', '?')} / {settings.get('model', '?')}")
        if save_settings(settings):
            print("    [✓] 系统设置已保存到云端")
        else:
            print("    [✗] 系统设置保存失败")
    else:
        print("\n[*] 未发现系统设置 JSON，保持云端默认")

    print("\n" + "=" * 60)
    print("迁移完成。打开 Supabase Dashboard → Table Editor 验证")
    print("=" * 60)


if __name__ == "__main__":
    main()
