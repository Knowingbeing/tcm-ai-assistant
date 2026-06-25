# Supabase 建库步骤

## 1. 注册并创建项目
1. 访问 https://supabase.com/dashboard 注册账号（可用 GitHub 登录）
2. New Project → 选区域（推荐 Singapore / Tokyo，离中国大陆近）
3. 设置 Database Password（妥善保存！）
4. 等待项目初始化完成（约 1-2 分钟）

## 2. 执行建表脚本
1. 左侧菜单 → **SQL Editor** → New query
2. 复制 `supabase/schema.sql` 全部内容粘贴进去
3. 点击 **Run**，底部应显示 "Success. No rows returned" 或版本表 1 行

## 3. 获取连接凭证
左侧菜单 → **Project Settings** → **API**，复制以下三个值：
- `Project URL`（形如 `https://xxxxx.supabase.co`）
- `anon public` key（前端可用的公钥）
- `service_role` key（**仅后端使用**，可绕过 RLS，慎用）

## 4. 配置到 Streamlit Cloud
在 Streamlit Cloud 的 app 页面 → **Settings** → **Secrets**，填入：
```toml
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...."
```

## 5. 本地开发配置
项目根目录创建 `.streamlit/secrets.toml`（已加入 .gitignore）：
```toml
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...."
```

## 6. 数据迁移（可选）
如需把旧的 `/tmp/tcm_records.json` 导入到 Supabase：
```bash
python scripts/migrate_json_to_supabase.py
```
脚本会读取项目根目录的 `tcm_records.json` 和 `tcm_settings.json` 并幂等导入。

## 7. 验证
- 启动 app：`streamlit run app.py`
- 在「智能问诊」保存一条记录
- 打开 Supabase Dashboard → **Table Editor** → `consultations`，应能看到该条记录
- 关闭并重启 app，记录仍在 → 升级成功 ✅
