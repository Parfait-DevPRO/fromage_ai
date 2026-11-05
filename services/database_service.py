"""Supabase-native database service (Zero SQLite).

Persists all conversations, messages, and cheese analyses directly in Supabase
with full relational integrity and cascade deletes.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4
from typing import Any

from config.settings import secret
from config.supabase_client import get_supabase_client


class DatabaseService:
    def __init__(self, *args, supabase_client=None, **kwargs):
        self.supabase = supabase_client if supabase_client is not None else get_supabase_client()
        if self.supabase is None:
            raise RuntimeError(
                "Connexion Supabase indisponible. Vérifiez SUPABASE_URL et SUPABASE_KEY dans .env ou .streamlit/secrets.toml."
            )

    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(timezone.utc)

    def load_conversations(self, user_id: str) -> list[dict[str, Any]]:
        """Load all conversations and nested messages/analyses for a user from Supabase."""
        try:
            res = (
                self.supabase.table("conversations")
                .select("*,messages(*,analyses(*))")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .execute()
            )
        except Exception as exc:
            raise RuntimeError(f"Impossible de charger les conversations depuis Supabase: {exc}") from exc

        rows = res.data or []
        conversations: list[dict[str, Any]] = []

        for conv in rows:
            raw_messages = conv.get("messages") or []
            # Sort messages chronologically
            sorted_messages = sorted(
                raw_messages,
                key=lambda m: m.get("created_at") or "",
            )

            messages: list[dict[str, Any]] = []
            for m in sorted_messages:
                raw_analyses = m.get("analyses") or []
                analysis_data = raw_analyses[0] if raw_analyses else None

                messages.append({
                    "id": m.get("id"),
                    "role": m.get("role"),
                    "content": m.get("content") or "",
                    "created_at": m.get("created_at"),
                    "analysis": analysis_data,
                })

            conversations.append({
                "id": conv["id"],
                "title": conv.get("title") or "Discussion",
                "created_at": conv.get("created_at"),
                "messages": messages,
            })

        return conversations

    def load_messages(self, conversation_id: str) -> list[dict[str, Any]]:
        """Load messages and linked analyses for a conversation."""
        try:
            res = (
                self.supabase.table("messages")
                .select("*,analyses(*)")
                .eq("conversation_id", conversation_id)
                .order("created_at", desc=False)
                .execute()
            )
        except Exception as exc:
            raise RuntimeError(f"Impossible de charger les messages depuis Supabase: {exc}") from exc

        messages: list[dict[str, Any]] = []
        for m in res.data or []:
            raw_analyses = m.get("analyses") or []
            messages.append({
                "id": m.get("id"),
                "role": m.get("role"),
                "content": m.get("content") or "",
                "created_at": m.get("created_at"),
                "analysis": raw_analyses[0] if raw_analyses else None,
            })
        return messages

    def create_conversation(self, user_id: str, title: str = "Nouvelle discussion") -> dict[str, Any]:
        """Create a new conversation record in Supabase."""
        conv_id = str(uuid4())
        try:
            res = (
                self.supabase.table("conversations")
                .insert({
                    "id": conv_id,
                    "user_id": user_id,
                    "title": title,
                })
                .execute()
            )
            created = (res.data or [{}])[0]
            return {
                "id": created.get("id", conv_id),
                "title": created.get("title", title),
                "created_at": created.get("created_at", self._utc_now().isoformat()),
                "messages": [],
            }
        except Exception as exc:
            raise RuntimeError(f"Impossible de créer la discussion dans Supabase: {exc}") from exc

    def update_conversation_title(self, conversation_id: str, title: str) -> None:
        """Update conversation title in Supabase."""
        clean_title = (title.strip() or "Analyse de fromage")[:60]
        try:
            self.supabase.table("conversations").update({"title": clean_title}).eq("id", conversation_id).execute()
        except Exception as exc:
            raise RuntimeError(f"Impossible de renommer la discussion dans Supabase: {exc}") from exc

    def delete_conversation(self, arg1: str, arg2: str | None = None) -> None:
        """Delete a conversation in Supabase (foreign key cascade automatically deletes messages & analyses)."""
        conversation_id = arg2 if arg2 is not None else arg1
        try:
            self.supabase.table("conversations").delete().eq("id", conversation_id).execute()
        except Exception as exc:
            raise RuntimeError(f"Impossible de supprimer la discussion dans Supabase: {exc}") from exc

    def purge_expired_conversations(self, user_id: str, retention_days: int = 3) -> set[str]:
        """Purge inactive conversations older than retention_days from Supabase."""
        cutoff = (self._utc_now() - timedelta(days=retention_days)).isoformat()
        try:
            expired = (
                self.supabase.table("conversations")
                .select("id")
                .eq("user_id", user_id)
                .lt("created_at", cutoff)
                .execute()
            )
            expired_ids = {str(row["id"]) for row in (expired.data or []) if row.get("id")}
            if expired_ids:
                self.supabase.table("conversations").delete().eq("user_id", user_id).in_("id", list(expired_ids)).execute()
            return expired_ids
        except Exception:
            return set()

    def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        image=None,
        analysis: dict | None = None,
    ) -> str:
        """Persist a chat message and linked cheese analysis directly in Supabase."""
        msg_id = str(uuid4())
        try:
            self.supabase.table("messages").insert({
                "id": msg_id,
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
            }).execute()

            if analysis:
                pred_class = str(analysis.get("predicted_class") or "inconnu")
                conf = float(analysis.get("confidence") or 0.0)
                probs = analysis.get("probabilities") or {}
                ver = str(analysis.get("model_version") or "1.0")

                self.supabase.table("analyses").insert({
                    "id": str(uuid4()),
                    "message_id": msg_id,
                    "predicted_class": pred_class,
                    "confidence": conf,
                    "probabilities": probs,
                    "model_version": ver,
                }).execute()

            return msg_id
        except Exception as exc:
            raise RuntimeError(f"Impossible d'enregistrer le message dans Supabase: {exc}") from exc
