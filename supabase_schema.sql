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
  created_at timestamptz default now()
);

create table if not exists public.messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references public.conversations(id) on delete cascade,
  role text not null check (role in ('user', 'assistant')),
  content text not null,
  created_at timestamptz default now()
);

create table if not exists public.analyses (
  id uuid primary key default gen_random_uuid(),
  message_id uuid not null references public.messages(id) on delete cascade,
  predicted_class text not null,
  confidence numeric not null,
  probabilities jsonb not null,
  model_version text not null,
  created_at timestamptz default now()
);
