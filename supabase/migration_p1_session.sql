-- ============================================================================
-- P1 Session 升级：添加 session_id、round_index、messages 字段
-- ============================================================================

-- 添加 session_id 字段
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS session_id text default '';
CREATE INDEX IF NOT EXISTS idx_consultations_session_id ON consultations (session_id);

-- 添加 round_index 字段
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS round_index integer default 0;

-- 添加 messages 字段（JSON 存储完整对话）
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS messages jsonb default '[]'::jsonb;

-- 更新 source 检查约束，允许更多来源
ALTER TABLE consultations DROP CONSTRAINT IF EXISTS consultations_source_check;
ALTER TABLE consultations ADD CONSTRAINT consultations_source_check CHECK (source in ('manual', 'api', 'imported', 'chat', 'draft'));

-- 添加 created_at 默认值更新
UPDATE consultations SET created_at = now() WHERE created_at IS NULL;
