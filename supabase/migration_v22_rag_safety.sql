-- v2.2 RAG、结构化输出与医疗安全字段
-- 可重复执行：用于从 v2.1 平滑升级 consultations 表。

alter table consultations add column if not exists structured_symptoms jsonb default '{}'::jsonb;
alter table consultations add column if not exists followups jsonb default '[]'::jsonb;
alter table consultations add column if not exists retrieval_ids jsonb default '[]'::jsonb;
alter table consultations add column if not exists prompt_version text default '';
alter table consultations add column if not exists model_name text default '';
alter table consultations add column if not exists structured_result jsonb default '{}'::jsonb;
alter table consultations add column if not exists safety_tags jsonb default '[]'::jsonb;
alter table consultations add column if not exists handoff_required boolean default false;
alter table consultations add column if not exists handoff_reason text default '';
alter table consultations add column if not exists model_status text default '';

create index if not exists idx_consultations_model_status on consultations (model_status);
create index if not exists idx_consultations_handoff on consultations (handoff_required);

insert into schema_version (version, description)
values (22, 'v2.2: rag retrieval ids, structured result, safety tags and handoff status')
on conflict (version) do nothing;
