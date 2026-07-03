# 数据库 Schema

## 1. 概览

项目使用 Supabase 托管的 PostgreSQL 15+ 数据库。Schema 定义分为两个文件：

| 文件 | 说明 | 版本 |
|------|------|------|
| `supabase/schema.sql` | 初始建表脚本（4 张表） | schema_version = 1 |
| `supabase/migration_p1_session.sql` | P1 多轮问诊迁移 | schema_version = 2 |

## 2. 初始 Schema (schema.sql)

### 2.1 patients 表 — 患者档案

```sql
create table if not exists patients (
    id           bigserial primary key,           -- 自增主键
    name         text        not null default '匿名',  -- 姓名，默认匿名
    age          integer,                          -- 年龄
    gender       text        check (gender in ('男', '女', '其他', '')),  -- 性别
    created_at   timestamptz not null default now()  -- 创建时间
);
create index if not exists idx_patients_created_at on patients (created_at desc);
```

**设计说明**：
- `name` 默认 `'匿名'`，允许用户不填姓名
- `gender` 使用 CHECK 约束限定值域，允许空字符串（未填写）
- 当前版本**未使用**此表（问诊记录直接在 consultations 表中存储 name/age/gender），为未来扩展预留

### 2.2 consultations 表 — 问诊记录（核心表）

```sql
create table if not exists consultations (
    id                   bigserial   primary key,           -- 自增主键
    patient_id           bigint      references patients(id) on delete set null,  -- 患者外键
    session_id           text        default '',            -- 多轮问诊会话 ID (P1 新增)
    round_index          integer     default 0,             -- 问诊轮次 (P1 新增)
    name                 text        not null default '匿名',  -- 患者姓名（冗余存储）
    age                  integer     default 0,             -- 年龄
    gender               text        default '',            -- 性别
    chief_complaint      text        not null,              -- 主诉（必填）
    symptoms             jsonb       not null default '[]'::jsonb,  -- 症状列表 (JSON 数组)
    tongue_sign          text        default '',            -- 舌象
    pulse_sign           text        default '',            -- 脉象
    syndrome             text        default '待辨证',       -- 证型
    syndrome_category    text        default '待分类',       -- 辨证体系
    formula              text        default '待推荐',       -- 推荐方剂
    formula_adjustment   text        default '',            -- 方剂加减
    treatment_principle  text        default '',            -- 治法
    analysis             text        default '',            -- 辨证分析
    confidence           integer     default 0 check (confidence between 0 and 100),  -- 置信度
    source               text        default 'manual' check (source in ('manual', 'api', 'imported', 'chat', 'draft')),  -- 数据来源
    messages             jsonb       default '[]'::jsonb,   -- 对话历史 (P1 新增)
    created_at           timestamptz not null default now()  -- 创建时间
);

-- 索引
create index if not exists idx_consultations_created_at on consultations (created_at desc);
create index if not exists idx_consultations_syndrome    on consultations (syndrome);
create index if not exists idx_consultations_patient_id  on consultations (patient_id);
```

**字段详解**：

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | bigserial | PK | 自增主键 |
| `patient_id` | bigint | FK → patients(id) | 患者外键，删除时置 NULL |
| `session_id` | text | - | 多轮问诊会话标识，单轮问诊为空字符串 |
| `round_index` | integer | - | 问诊轮次，0 = 首轮 |
| `name` | text | NOT NULL, default '匿名' | 患者姓名（冗余，便于查询） |
| `age` | integer | default 0 | 年龄 |
| `gender` | text | - | 性别 |
| `chief_complaint` | text | NOT NULL | 主诉（唯一必填字段） |
| `symptoms` | jsonb | NOT NULL, default '[]' | 症状列表，JSON 数组格式 |
| `tongue_sign` | text | - | 舌象描述 |
| `pulse_sign` | text | - | 脉象描述 |
| `syndrome` | text | default '待辨证' | AI 辨证结果 |
| `syndrome_category` | text | default '待分类' | 辨证体系（六经/脏腑等） |
| `formula` | text | default '待推荐' | 推荐方剂 |
| `formula_adjustment` | text | - | 方剂加减建议 |
| `treatment_principle` | text | - | 治法 |
| `analysis` | text | - | 辨证分析文本 |
| `confidence` | integer | CHECK [0,100] | 置信度百分比 |
| `source` | text | CHECK enum | 数据来源 |
| `messages` | jsonb | default '[]' | 完整对话历史（OpenAI 格式） |
| `created_at` | timestamptz | NOT NULL, default now() | 创建时间 |

**source 枚举值**：

| 值 | 说明 |
|----|------|
| `manual` | 手动录入（默认） |
| `api` | API 调用产生 |
| `imported` | 从 JSON 迁移导入 |
| `chat` | 多轮对话问诊产生 |
| `draft` | 草稿/诊断测试写入 |

**索引设计**：
- `idx_consultations_created_at`：按时间倒序查询（列表展示）
- `idx_consultations_syndrome`：按证型统计（数据分析 Tab）
- `idx_consultations_patient_id`：按患者查询（预留）

### 2.3 settings 表 — 系统设置（单行表）

```sql
create table if not exists settings (
    id          integer     primary key default 1 check (id = 1),  -- 固定 id=1
    api_key     text        default '',       -- LLM API Key
    provider    text        default 'DeepSeek',  -- 服务商
    model       text        default '',       -- 模型名称
    updated_at  timestamptz not null default now()  -- 更新时间
);
insert into settings (id, api_key, provider, model)
values (1, '', 'DeepSeek', '')
on conflict (id) do nothing;
```

**设计说明**：
- 使用 `CHECK (id = 1)` 约束确保表中只有一行记录
- 通过 `upsert` 操作更新配置
- `on conflict (id) do nothing` 确保初始化脚本可重复执行

### 2.4 schema_version 表 — 迁移版本管理

```sql
create table if not exists schema_version (
    version     integer     primary key,     -- 版本号
    description text,                          -- 版本描述
    applied_at  timestamptz not null default now()  -- 应用时间
);
insert into schema_version (version, description)
values (1, 'init: patients / consultations / settings / schema_version')
on conflict (version) do nothing;
```

### 2.5 RLS 策略

```sql
-- 关闭行级安全（单租户场景）
alter table patients       disable row level security;
alter table consultations  disable row level security;
alter table settings       disable row level security;
alter table schema_version disable row level security;
```

**设计说明**：项目定位为个人/家庭使用，单租户场景下 RLS 增加配置复杂度但无实际安全收益。多用户场景需重新启用 RLS 并添加 policy。

## 3. P1 迁移脚本 (migration_p1_session.sql)

```sql
-- P1 Session 升级：添加 session_id、round_index、messages 字段
-- 迁移版本：schema_version = 2

-- 1. 添加 session_id 字段
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS session_id text default '';
CREATE INDEX IF NOT EXISTS idx_consultations_session_id ON consultations (session_id);

-- 2. 添加 round_index 字段
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS round_index integer default 0;

-- 3. 添加 messages 字段（JSON 存储完整对话）
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS messages jsonb default '[]'::jsonb;

-- 4. 更新 source 检查约束，允许 'chat' 和 'draft'
ALTER TABLE consultations DROP CONSTRAINT IF EXISTS consultations_source_check;
ALTER TABLE consultations ADD CONSTRAINT consultations_source_check 
    CHECK (source in ('manual', 'api', 'imported', 'chat', 'draft'));

-- 5. 修复 NULL 的 created_at
UPDATE consultations SET created_at = now() WHERE created_at IS NULL;
```

**迁移要点**：
- 使用 `ADD COLUMN IF NOT EXISTS` 确保可重复执行
- 新增 `idx_consultations_session_id` 索引支持按会话查询
- 重建 `source` 约束以增加 `'chat'` 和 `'draft'` 两个新枚举值
- 修复历史数据中可能存在的 `NULL` created_at

## 4. ER 关系图

```
┌─────────────┐         ┌──────────────────────────┐
│  patients   │    1    │     consultations        │
│─────────────│◄────────│──────────────────────────│
│ id (PK)     │  0..N   │ id (PK)                  │
│ name        │         │ patient_id (FK, nullable)│
│ age         │         │ session_id               │
│ gender      │         │ round_index              │
│ created_at  │         │ name (冗余)               │
└─────────────┘         │ age (冗余)                │
                        │ gender (冗余)             │
                        │ chief_complaint (NOT NULL)│
                        │ symptoms (jsonb)          │
                        │ tongue_sign              │
                        │ pulse_sign               │
                        │ syndrome                 │
                        │ syndrome_category        │
                        │ formula                  │
                        │ formula_adjustment       │
                        │ treatment_principle      │
                        │ analysis                 │
                        │ confidence (0-100)       │
                        │ source (enum)            │
                        │ messages (jsonb)         │
                        │ created_at               │
                        └──────────────────────────┘
                                   │
                                   │ session_id 关联
                                   ▼
                        ┌──────────────────────────┐
                        │  同一 session_id 的多条    │
                        │  consultations 记录 =      │
                        │  一个多轮问诊会话          │
                        │                          │
                        │  round_index=0: 首轮      │
                        │  round_index=1: 第1轮追问  │
                        │  round_index=2: 第2轮追问  │
                        └──────────────────────────┘

┌─────────────┐         ┌─────────────┐
│  settings   │         │schema_version│
│─────────────│         │─────────────│
│ id=1 (单行) │         │ version (PK) │
│ api_key     │         │ description  │
│ provider    │         │ applied_at   │
│ model       │         └─────────────┘
│ updated_at  │
└─────────────┘
```

## 5. messages 字段格式 (JSONB)

多轮问诊的对话历史以 OpenAI 消息格式存储：

```json
[
  {
    "role": "system",
    "content": "你是一位经验丰富的中医师..."
  },
  {
    "role": "user",
    "content": "主诉：头痛三天\n症状：恶寒、无汗\n舌象：舌淡苔白\n脉象：脉浮紧"
  },
  {
    "role": "assistant",
    "content": "根据您描述的症状..."
  },
  {
    "role": "user",
    "content": "我的舌象是舌淡苔白"  // 追问回答
  },
  {
    "role": "assistant",
    "content": "综合以上信息，辨证为..."
  }
]
```

## 6. 数据量估算

| 场景 | 单条记录大小 | 1000 条记录 | Supabase 免费额度 (500MB) |
|------|-------------|-------------|--------------------------|
| 单轮问诊 | ~1-2 KB | ~1-2 MB | 可存储 ~25 万条 |
| 多轮问诊 (3 轮) | ~3-5 KB | ~3-5 MB | 可存储 ~10 万条 |

**结论**：个人/家庭使用场景下，Supabase 免费额度完全足够。

## 7. 与 SQLite 旧 Schema 的对比

| 对比项 | SQLite (database.py) | Supabase (schema.sql + migration) |
|--------|---------------------|-----------------------------------|
| 表数量 | 7 张（含关联表） | 4 张（扁平化设计） |
| 证型/方剂存储 | 独立表 + 外键 | 嵌入 consultations 文本字段 |
| 问诊记录字段 | 11 个 | 20 个（含 P1 扩展） |
| 多轮问诊支持 | ❌ | ✅ (session_id + round_index + messages) |
| 外键约束 | 3 个 | 1 个 (patient_id, nullable) |
| 索引 | 无 | 4 个 |
| RLS | N/A | 显式禁用（单租户） |
| 知识库存储 | 数据库表 | 内存常量 (tcm_data.py) |
