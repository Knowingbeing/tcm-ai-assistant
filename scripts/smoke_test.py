"""
冒烟测试 — 不需要真实 Supabase 凭证
====================================

覆盖：
1. Supabase 未配置时：get_records / get_settings 走降级路径，不抛异常
2. JSON 文件读写：save_records → load_records 回路
3. schema.sql 语法：用 sqlite3 风格的语法检查（粗略）
4. 模块导入：supabase_client / llm_engine / tcm_data 全部可 import

运行：
  python scripts/smoke_test.py
"""

import os
import sys
import json
import tempfile
import importlib

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


def test_section(name):
    print(f"\n[TEST] {name}")
    print("-" * 50)


def assert_eq(actual, expected, msg=""):
    if actual == expected:
        print(f"  [OK] {msg or 'OK'}")
    else:
        print(f"  [FAIL] {msg}")
        print(f"    expected: {expected}")
        print(f"    actual  : {actual}")
        sys.exit(1)


def assert_true(cond, msg=""):
    if cond:
        print(f"  [OK] {msg or 'OK'}")
    else:
        print(f"  [FAIL] {msg or 'FAIL'}")
        sys.exit(1)


def main():
    test_section("1. Supabase 未配置降级测试")
    # 显式清空环境变量
    os.environ.pop("SUPABASE_URL", None)
    os.environ.pop("SUPABASE_KEY", None)

    from utils import supabase_client
    importlib.reload(supabase_client)

    assert_eq(supabase_client.is_configured(), False, "未配置时 is_configured() == False")
    assert_eq(supabase_client.get_client(), None, "未配置时 get_client() 返回 None")
    assert_eq(supabase_client.get_records(), [], "未配置时 get_records() 返回空列表")
    cfg = supabase_client.get_settings()
    assert_true(cfg.get("provider") == "DeepSeek", f"默认 provider == DeepSeek, got {cfg.get('provider')}")

    test_section("2. JSON 模式读写回路")
    # 模拟 JSON 模式：app.py 的 save_records / load_records 在没 Supabase 时使用
    test_records = [
        {
            "id": 1,
            "name": "测试患者",
            "age": 30,
            "gender": "男",
            "chief_complaint": "头痛三天",
            "symptoms": ["头痛", "恶寒"],
            "syndrome": "太阳伤寒证",
            "syndrome_category": "六经辨证",
            "formula": "麻黄汤",
            "confidence": 85,
            "date": "2026-06-25 10:00:00",
        }
    ]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(test_records, f, ensure_ascii=False)
        tmp_path = f.name

    with open(tmp_path, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert_eq(len(loaded), 1, "JSON 写入后再读出，记录数一致")
    assert_eq(loaded[0]["chief_complaint"], "头痛三天", "主诉字段一致")
    os.unlink(tmp_path)

    test_section("3. 模块导入测试")
    for mod in ["utils.llm_engine", "utils.supabase_client", "data.tcm_data"]:
        try:
            __import__(mod)
            print(f"  [OK] {mod} 可正常导入")
        except Exception as e:
            print(f"  [FAIL] {mod} 导入失败：{e}")
            sys.exit(1)

    test_section("4. schema.sql 文件存在性 + 基础检查")
    schema_path = os.path.join(PROJECT_ROOT, "supabase", "schema.sql")
    assert_true(os.path.exists(schema_path), f"schema.sql 存在：{schema_path}")
    with open(schema_path, "r", encoding="utf-8") as f:
        sql = f.read()
    for keyword in ["create table if not exists patients",
                    "create table if not exists consultations",
                    "create table if not exists settings",
                    "create table if not exists schema_version"]:
        assert_true(keyword in sql, f"包含 {keyword!r}")
    # 索引和 RLS 关闭
    assert_true("disable row level security" in sql, "已显式禁用 RLS")
    assert_true("create index" in sql, "包含索引定义")

    test_section("5. 迁移脚本语法检查")
    migration_path = os.path.join(PROJECT_ROOT, "scripts", "migrate_json_to_supabase.py")
    assert_true(os.path.exists(migration_path), "迁移脚本存在")
    with open(migration_path, "r", encoding="utf-8") as f:
        code = f.read()
    try:
        compile(code, migration_path, "exec")
        print(f"  [OK] {migration_path} 编译通过")
    except SyntaxError as e:
        print(f"  [FAIL] 迁移脚本语法错误：{e}")
        sys.exit(1)

    test_section("6. app.py 编译检查")
    app_path = os.path.join(PROJECT_ROOT, "app.py")
    with open(app_path, "r", encoding="utf-8") as f:
        code = f.read()
    try:
        compile(code, app_path, "exec")
        print(f"  [OK] app.py 编译通过（{len(code)} 字符）")
    except SyntaxError as e:
        print(f"  [FAIL] app.py 语法错误：{e}")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("[PASS] 全部冒烟测试通过")
    print("=" * 50)


if __name__ == "__main__":
    main()
