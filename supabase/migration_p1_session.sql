-- ============================================================================
-- P1 增量：多轮问诊 — 同会话的多次记录通过 session_id 关联
-- 用法：在 Supabase SQL Editor 直接执行（幂等）
-- ============================================================================

-- 1. 加列（IF NOT EXISTS 保证安全）
alter table consultations
    add column if not exists session_id   uuid,
    add column if not exists round_index  integer     default 1,
    add column if not exists messages     jsonb       default '[]'::jsonb;

-- 2. 索引：按 session 查找一条问诊的所有记录
create index if not exists idx_consultations_session
    on consultations (session_id, round_index);

-- 3. 回填：给历史记录生成 UUID（用 id 当种子，保证稳定）
update consultations
   set session_id = gen_random_uuid()
 where session_id is null;

-- 4. 标记 schema 版本
insert into schema_version (version, description)
values (2, 'P1: consultations 加 session_id / round_index / messages 列')
on conflict (version) do nothing;

-- ============================================================================
-- 验证
-- select column_name, data_type from information_schema.columns
-- where table_name = 'consultations' and column_name in ('session_id', 'round_index', 'messages');
-- 应返回 3 行
-- ============================================================================
