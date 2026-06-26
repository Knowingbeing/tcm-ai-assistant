-- ============================================================================
-- 中医AI智能问诊助手 — Supabase Schema
-- 适用：PostgreSQL 15+ (Supabase 托管)
-- 作用：将 /tmp/tcm_records.json 与 tcm_settings.json 替换为云端持久化
-- 策略：单租户（个人/家庭使用），anon key 即可读写，无 RLS 限制
-- ============================================================================

-- 1. 患者档案（可选：用户不填姓名时用"匿名"）
create table if not exists patients (
    id           bigserial primary key,
    name         text        not null default '匿名',
    age          integer,
    gender       text        check (gender in ('男', '女', '其他', '')),
    created_at   timestamptz not null default now()
);
create index if not exists idx_patients_created_at on patients (created_at desc);

-- 2. 问诊记录（事实表）
create table if not exists consultations (
    id                   bigserial   primary key,
    patient_id           bigint      references patients(id) on delete set null,
    session_id           text        default '',
    round_index          integer     default 0,
    name                 text        not null default '匿名',
    age                  integer     default 0,
    gender               text        default '',
    chief_complaint      text        not null,
    symptoms             jsonb       not null default '[]'::jsonb,
    tongue_sign          text        default '',
    pulse_sign           text        default '',
    syndrome             text        default '待辨证',
    syndrome_category    text        default '待分类',
    formula              text        default '待推荐',
    formula_adjustment   text        default '',
    treatment_principle  text        default '',
    analysis             text        default '',
    confidence           integer     default 0 check (confidence between 0 and 100),
    source               text        default 'manual' check (source in ('manual', 'api', 'imported', 'chat', 'draft')),
    messages             jsonb       default '[]'::jsonb,
    created_at           timestamptz not null default now()
);
create index if not exists idx_consultations_created_at on consultations (created_at desc);
create index if not exists idx_consultations_syndrome    on consultations (syndrome);
create index if not exists idx_consultations_patient_id  on consultations (patient_id);

-- 3. 系统设置（API Key、provider、model）
-- 单行表：用固定 id = 1 存当前配置，避免到处建配置管理
create table if not exists settings (
    id          integer     primary key default 1 check (id = 1),
    api_key     text        default '',
    provider    text        default 'DeepSeek',
    model       text        default '',
    updated_at  timestamptz not null default now()
);
insert into settings (id, api_key, provider, model)
values (1, '', 'DeepSeek', '')
on conflict (id) do nothing;

-- 4. 迁移版本表（便于后续平滑升级）
create table if not exists schema_version (
    version     integer     primary key,
    description text,
    applied_at  timestamptz not null default now()
);
insert into schema_version (version, description)
values (1, 'init: patients / consultations / settings / schema_version')
on conflict (version) do nothing;

-- 5. 关闭 RLS（单租户场景，简化配置；多用户场景需重开 + policy）
alter table patients       disable row level security;
alter table consultations  disable row level security;
alter table settings       disable row level security;
alter table schema_version disable row level security;

-- ============================================================================
-- 验证查询（执行后应返回 1 行）
-- select * from schema_version order by version desc limit 1;
-- ============================================================================
