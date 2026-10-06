-- Fromazy_AI: Supabase persistence with LOCAL username/password authentication.
-- Run this script once in Supabase > SQL Editor. It does not use Supabase Auth.

create table if not exists public.users (
  id uuid primary key,
  username text not null,
  display_name text,
  created_at timestamptz default now()
);

-- Safe migration from the former Supabase Auth-based schema.
alter table public.users drop constraint if exists users_id_fkey;
alter table public.users add column if not exists username text;
alter table public.users add column if not exists display_name text;
drop trigger if exists on_auth_user_created on auth.users;
drop function if exists public.handle_new_user();
create unique index if not exists users_username_lower_unique on public.users (lower(username));

create table if not exists public.conversations (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users(id) on delete cascade,
  title text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
alter table public.conversations add column if not exists updated_at timestamptz;
create index if not exists conversations_user_created_idx on public.conversations (user_id, created_at desc);

create table if not exists public.messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references public.conversations(id) on delete cascade,
  role text not null check (role in ('user', 'assistant')),
  content text not null,
  has_image boolean not null default false,
  created_at timestamptz not null default now()
);
alter table public.messages add column if not exists has_image boolean not null default false;
create index if not exists messages_conversation_created_idx on public.messages (conversation_id, created_at);

-- Preserve recent activity when migrating an existing conversations table.
update public.conversations c
set updated_at = greatest(
  c.created_at,
  coalesce((select max(m.created_at) from public.messages m where m.conversation_id = c.id), c.created_at)
)
where c.updated_at is null;
alter table public.conversations alter column updated_at set default now();
alter table public.conversations alter column updated_at set not null;
create index if not exists conversations_updated_at_idx on public.conversations (updated_at);

create table if not exists public.analyses (
  id uuid primary key default gen_random_uuid(),
  message_id uuid not null references public.messages(id) on delete cascade,
  predicted_class text not null,
  confidence numeric not null,
  probabilities jsonb not null,
  model_version text not null,
  is_cheese boolean not null default true,
  message text,
  created_at timestamptz not null default now()
);
alter table public.analyses add column if not exists is_cheese boolean not null default true;
alter table public.analyses add column if not exists message text;

-- These tables are written by the Streamlit server with its server-only
-- Supabase secret key. Do not expose user/account data to publishable clients.
alter table public.users enable row level security;
alter table public.conversations enable row level security;
alter table public.messages enable row level security;
alter table public.analyses enable row level security;

-- Remove permissive policies from older setups. The server key bypasses RLS;
-- public client roles must not read or write local-password account data.
drop policy if exists "Allow all on users" on public.users;
drop policy if exists "Allow all on conversations" on public.conversations;
drop policy if exists "Allow all on messages" on public.messages;
drop policy if exists "Allow all on analyses" on public.analyses;

revoke all on public.users, public.conversations, public.messages, public.analyses from anon, authenticated;
grant usage on schema public to service_role;
grant all on public.users, public.conversations, public.messages, public.analyses to service_role;

-- Cleanup conversations after 3 days without activity. The app refreshes
-- updated_at whenever it saves a message; older rows use created_at.
create or replace function public.purge_expired_conversations()
returns void
language sql
security definer
set search_path = public
as $function$
  delete from public.conversations
  where coalesce(updated_at, created_at) < now() - interval '3 days';
$function$;
revoke all on function public.purge_expired_conversations() from public, anon, authenticated, service_role;

-- Supabase Cron uses pg_cron. Run the cleanup hourly (at most one hour after expiry).
create extension if not exists pg_cron;
do $block$
declare
  existing_job_id bigint;
begin
  select jobid into existing_job_id
  from cron.job
  where jobname = 'fromazy-purge-expired-conversations';
  if existing_job_id is not null then
    perform cron.unschedule(existing_job_id);
  end if;
end
$block$;
select cron.schedule(
  'fromazy-purge-expired-conversations',
  '0 * * * *',
  'select public.purge_expired_conversations();'
);

-- Refresh the PostgREST schema cache after applying these table changes.
notify pgrst, 'reload schema';
