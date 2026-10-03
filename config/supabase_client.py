"""Unified Supabase client adapter and connection diagnostics.

Supports both standard JWT keys (anon / service_role) and new publishable keys (sb_publishable_...).
"""
from __future__ import annotations

import re
from typing import Any
import requests
from config.settings import secret


class UnifiedSupabaseClient:
    """Provides a consistent .table(name) interface regardless of underlying client."""

    def __init__(self, raw_client, is_postgrest: bool = False):
        self._raw = raw_client
        self.is_postgrest = is_postgrest

    def table(self, table_name: str):
        return self._raw.table(table_name)

    @property
    def auth(self):
        return getattr(self._raw, "auth", None)


def clean_supabase_url(url: str) -> str:
    """Normalize Supabase URL."""
    if not url:
        return ""
    url = url.strip().rstrip("/")
    if not url.startswith("http://") and not url.startswith("https://"):
        url = f"https://{url}"
    return url


def clean_supabase_key(key: str) -> str:
    """Normalize Supabase key."""
    if not key:
        return ""
    return key.strip().strip('"').strip("'").strip()


def get_supabase_client(custom_url: str | None = None, custom_key: str | None = None) -> UnifiedSupabaseClient | None:
    """Create and return a unified Supabase client, or None if configuration is missing/invalid."""
    url = clean_supabase_url(custom_url or secret("SUPABASE_URL"))
    key = clean_supabase_key(custom_key or secret("SUPABASE_KEY"))

    if not url or not key:
        return None

    # Try standard supabase-py create_client first if key is a valid JWT
    is_jwt = bool(re.match(r"^[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*$", key))
    if is_jwt:
        try:
            from supabase import create_client
            client = create_client(url, key)
            return UnifiedSupabaseClient(client, is_postgrest=False)
        except Exception:
            pass

    # Use PostgREST client directly (supports sb_publishable_..., sb_secret_..., and JWTs)
    try:
        from postgrest import SyncPostgrestClient
        rest_url = f"{url}/rest/v1"
        headers = {
            "apikey": key,
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
        # New sb_publishable_/sb_secret_ API keys are not JWTs and belong only
        # in `apikey`. Legacy anon/service_role JWTs also use Authorization.
        if not key.startswith(("sb_publishable_", "sb_secret_")):
            headers["Authorization"] = f"Bearer {key}"
        postgrest_client = SyncPostgrestClient(rest_url, headers=headers)
        return UnifiedSupabaseClient(postgrest_client, is_postgrest=True)
    except Exception:
        return None


def test_supabase_connection(custom_url: str | None = None, custom_key: str | None = None) -> dict[str, Any]:
    """Test connection to Supabase and return diagnostic information."""
    url = clean_supabase_url(custom_url or secret("SUPABASE_URL"))
    key = clean_supabase_key(custom_key or secret("SUPABASE_KEY"))

    if not url:
        return {
            "ok": False,
            "status": "missing_url",
            "title": "URL Supabase manquante",
            "message": "SUPABASE_URL n'est pas configuré. Veuillez indiquer l'URL de votre projet Supabase (ex: https://xyz.supabase.co).",
            "sql_fix": None,
        }

    if not key:
        return {
            "ok": False,
            "status": "missing_key",
            "title": "Clé Supabase manquante",
            "message": "SUPABASE_KEY n'est pas configuré. Veuillez renseigner la clé API Supabase.",
            "sql_fix": None,
        }

    # 1. Ping the instance
    try:
        ping = requests.get(f"{url}/auth/v1/health", headers={"apikey": key}, timeout=5)
    except Exception as exc:
        return {
            "ok": False,
            "status": "unreachable",
            "title": "Serveur Supabase injoignable",
            "message": f"Impossible de contacter {url} ({exc}). Vérifiez votre connexion Internet et l'URL du projet.",
            "sql_fix": None,
        }

    # 2. Check read on tables via PostgREST
    headers = {
        "apikey": key,
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    if not key.startswith(("sb_publishable_", "sb_secret_")):
        headers["Authorization"] = f"Bearer {key}"

    try:
        resp = requests.get(f"{url}/rest/v1/users?select=id&limit=1", headers=headers, timeout=5)
    except Exception as exc:
        return {
            "ok": False,
            "status": "network_error",
            "title": "Erreur réseau Supabase",
            "message": str(exc),
            "sql_fix": None,
        }

    if resp.status_code == 401 and "Secret API key required" in resp.text:
        return {
            "ok": False,
            "status": "key_type_error",
            "title": "Type de clé API non compatible pour les requêtes directes",
            "message": "La clé fournie requiert un droit secret ou la clé JWT anon publique standard (commençant par eyJ...).",
            "sql_fix": None,
        }

    if resp.status_code == 404:
        return {
            "ok": False,
            "status": "missing_tables",
            "title": "Tables Supabase absentes",
            "message": "Les tables de Fromazy_AI (users, conversations, messages, analyses) ne sont pas encore créées dans ce projet Supabase.",
            "sql_fix": RLS_FIX_SQL,
        }

    # 3. Test insert capability to detect Row-Level Security (RLS) restrictions
    test_id = "00000000-0000-0000-0000-000000000000"
    try:
        insert_test = requests.post(
            f"{url}/rest/v1/users",
            json={"id": test_id, "username": "_conn_check_", "display_name": "Check"},
            headers=headers,
            timeout=5,
        )
        if insert_test.status_code in (200, 201):
            # Clean up test row
            requests.delete(f"{url}/rest/v1/users?id=eq.{test_id}", headers=headers, timeout=5)
            return {
                "ok": True,
                "status": "connected",
                "title": "Supabase connecté et opérationnel",
                "message": "La connexion à Supabase est établie avec succès. Lecture et écriture autorisées.",
                "sql_fix": None,
            }
        if insert_test.status_code == 401 or "42501" in insert_test.text or "row-level security" in insert_test.text:
            return {
                "ok": False,
                "status": "rls_error",
                "title": "Sécurité RLS active dans Supabase",
                "message": (
                    "La base Supabase répond bien, mais les politiques de sécurité (Row Level Security - RLS) "
                    "bloquent l'enregistrement des données pour votre clé d'API. "
                    "Exécutez le script SQL ci-dessous dans l'éditeur SQL de Supabase pour autoriser l'accès."
                ),
                "sql_fix": RLS_FIX_SQL,
            }
        if "duplicate key" in insert_test.text or "unique constraint" in insert_test.text:
            return {
                "ok": True,
                "status": "connected",
                "title": "Supabase connecté",
                "message": "Connexion établie avec succès.",
                "sql_fix": None,
            }
    except Exception:
        pass

    # Read succeeded even if write test had an unexpected code
    if resp.status_code == 200:
        return {
            "ok": True,
            "status": "connected_read_only",
            "title": "Supabase connecté (Lecture OK)",
            "message": "Connexion à Supabase active. Si l'enregistrement échoue, vérifiez les politiques RLS.",
            "sql_fix": RLS_FIX_SQL,
        }

    return {
        "ok": False,
        "status": "unknown_error",
        "title": "Erreur Supabase",
        "message": f"Code HTTP {resp.status_code}: {resp.text[:150]}",
        "sql_fix": RLS_FIX_SQL,
    }


RLS_FIX_SQL = """-- Script d'activation des droits pour Fromazy_AI dans Supabase
-- À copier-coller dans Supabase > SQL Editor > Run

-- 1. Tables principales
create table if not exists public.users (
  id uuid primary key,
  username text not null,
  display_name text,
  created_at timestamptz default now()
);

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

-- 2. Autorisation d'accès (RLS)
alter table public.users enable row level security;
alter table public.conversations enable row level security;
alter table public.messages enable row level security;
alter table public.analyses enable row level security;

drop policy if exists "Allow all on users" on public.users;
create policy "Allow all on users" on public.users for all using (true) with check (true);

drop policy if exists "Allow all on conversations" on public.conversations;
create policy "Allow all on conversations" on public.conversations for all using (true) with check (true);

drop policy if exists "Allow all on messages" on public.messages;
create policy "Allow all on messages" on public.messages for all using (true) with check (true);

drop policy if exists "Allow all on analyses" on public.analyses;
create policy "Allow all on analyses" on public.analyses for all using (true) with check (true);
"""
