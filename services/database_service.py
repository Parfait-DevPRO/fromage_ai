"""Unified Database Service for local SQLite and Supabase Cloud synchronization.

Ensures the application works instantly offline/locally, while continuously syncing
conversations, messages, and cheese analyses to Supabase when connected.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4
from typing import Any

from config.settings import BASE_DIR, secret
from config.supabase_client import get_supabase_client

DATABASE_PATH = BASE_DIR / "data" / "cheese_ai.db"


class DatabaseService:
    def __init__(self, db_path: Path = DATABASE_PATH, supabase_client=None):
        self.db_path = Path(db_path)
        self.supabase = supabase_client if supabase_client is not None else get_supabase_client()
        self._supports_updated_at: bool | None = None
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_sqlite()

    def _require_supabase(self):
        key = secret("SUPABASE_KEY")
        if key.startswith("sb_publishable_"):
            raise RuntimeError(
                "SUPABASE_KEY est une cle publishable, qui ne peut pas ecrire dans les tables. "
                "Configurez une cle serveur sb_secret_ dans .streamlit/secrets.toml puis redemarrez Streamlit."
            )
        if self.supabase is None:
            raise RuntimeError(
                "Connexion Supabase indisponible. Vérifiez SUPABASE_URL, "
                "la clé serveur SUPABASE_KEY et le schéma SQL."
            )

    def _connection(self):
        return sqlite3.connect(self.db_path)

    def _has_updated_at(self) -> bool:
        if self._supports_updated_at is None:
            try:
                self.supabase.table("conversations").select("updated_at").limit(0).execute()
                self._supports_updated_at = True
            except Exception:
                # Older deployed schemas may not have been migrated yet.
                self._supports_updated_at = False
        return self._supports_updated_at

    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(timezone.utc)

    def purge_expired_conversations(self, user_id: str, retention_days: int = 3) -> set[str]:
        """Remove conversations inactive for the retention period from Supabase and SQLite."""
        self._require_supabase()
        cutoff = (self._utc_now() - timedelta(days=retention_days)).isoformat()
        time_column = "updated_at" if self._has_updated_at() else "created_at"
        try:
            expired = (
                self.supabase.table("conversations")
                .select("id")
                .eq("user_id", user_id)
                .lt(time_column, cutoff)
                .execute()
            )
            expired_ids = {str(row["id"]) for row in (expired.data or []) if row.get("id")}
            if time_column == "created_at":
                # Before the updated_at migration, use the latest message to
                # distinguish an old but recently active chat from an idle one.
                cutoff_dt = self._utc_now() - timedelta(days=retention_days)
                for conversation_id in tuple(expired_ids):
                    latest = (
                        self.supabase.table("messages")
                        .select("created_at")
                        .eq("conversation_id", conversation_id)
                        .order("created_at", desc=True)
                        .limit(1)
                        .execute()
                    )
                    if latest.data:
                        last_activity = datetime.fromisoformat(
                            str(latest.data[0]["created_at"]).replace("Z", "+00:00")
                        )
                        if last_activity.tzinfo is None:
                            last_activity = last_activity.replace(tzinfo=timezone.utc)
                        if last_activity >= cutoff_dt:
                            expired_ids.discard(conversation_id)
            if expired_ids:
                self.supabase.table("conversations").delete().eq("user_id", user_id).in_("id", list(expired_ids)).execute()
        except Exception as exc:
            raise RuntimeError("Impossible de nettoyer les anciennes conversations dans Supabase.") from exc

        # Keep the local cache in step with the remote delete.
        with self._connection() as conn:
            if expired_ids:
                for conversation_id in expired_ids:
                    conn.execute("DELETE FROM local_analyses WHERE message_id IN (SELECT id FROM local_messages WHERE conversation_id = ?)", (conversation_id,))
                    conn.execute("DELETE FROM local_messages WHERE conversation_id = ?", (conversation_id,))
                    conn.execute("DELETE FROM local_conversations WHERE id = ? AND user_id = ?", (conversation_id, user_id))
        return expired_ids

    def _init_sqlite(self):
        with self._connection() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS local_conversations (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS local_messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL REFERENCES local_conversations(id) ON DELETE CASCADE,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                has_image INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS local_analyses (
                id TEXT PRIMARY KEY,
                message_id TEXT NOT NULL REFERENCES local_messages(id) ON DELETE CASCADE,
                predicted_class TEXT NOT NULL,
                confidence REAL NOT NULL,
                probabilities TEXT NOT NULL,
                model_version TEXT NOT NULL,
                is_cheese INTEGER NOT NULL DEFAULT 1,
                message TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """)
            local_analysis_columns = {row[1] for row in conn.execute("PRAGMA table_info(local_analyses)")}
            if "is_cheese" not in local_analysis_columns:
                conn.execute("ALTER TABLE local_analyses ADD COLUMN is_cheese INTEGER NOT NULL DEFAULT 1")
            if "message" not in local_analysis_columns:
                conn.execute("ALTER TABLE local_analyses ADD COLUMN message TEXT")
            conn.execute(
                "DELETE FROM local_analyses WHERE rowid NOT IN "
                "(SELECT MIN(rowid) FROM local_analyses GROUP BY message_id)"
            )
            conn.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS local_analyses_message_unique_idx "
                "ON local_analyses(message_id)"
            )

    def load_conversations(self, user_id: str) -> list[dict[str, Any]]:
        """Load all conversations for a user. Syncs with Supabase if reachable."""
        self._require_supabase()
        # 1. First attempt to pull conversations from Supabase if connected
        if self.supabase:
            try:
                res = self.supabase.table("conversations").select("*").eq("user_id", user_id).execute()
                remote_rows = res.data or []
                remote_ids = {str(row["id"]) for row in remote_rows if row.get("id")}
                with self._connection() as conn:
                    for row in remote_rows:
                        conn.execute(
                            """
                            INSERT INTO local_conversations (id, user_id, title, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?)
                            ON CONFLICT(id) DO UPDATE SET title = excluded.title, updated_at = excluded.updated_at
                            """,
                            (
                                row.get("id"),
                                row.get("user_id"),
                                row.get("title") or "Discussion",
                                row.get("created_at") or self._utc_now().isoformat(),
                                row.get("updated_at") or row.get("created_at") or self._utc_now().isoformat(),
                            ),
                        )
                    cached_ids = {
                        str(row[0]) for row in conn.execute(
                            "SELECT id FROM local_conversations WHERE user_id = ?", (user_id,)
                        ).fetchall()
                    }
                    for stale_id in cached_ids - remote_ids:
                        conn.execute("DELETE FROM local_analyses WHERE message_id IN (SELECT id FROM local_messages WHERE conversation_id = ?)", (stale_id,))
                        conn.execute("DELETE FROM local_messages WHERE conversation_id = ?", (stale_id,))
                        conn.execute("DELETE FROM local_conversations WHERE id = ? AND user_id = ?", (stale_id, user_id))
            except Exception as exc:
                raise RuntimeError("Impossible de lire les conversations dans Supabase.") from exc

        # 2. Return from local database (guaranteed fast and reliable)
        with self._connection() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT id, user_id, title, created_at, updated_at FROM local_conversations WHERE user_id = ? ORDER BY updated_at DESC, created_at DESC",
                (user_id,),
            ).fetchall()

        conversations = []
        for r in rows:
            conv_id = r["id"]
            messages = self.load_messages(conv_id)
            conversations.append({
                "id": conv_id,
                "title": r["title"],
                "created_at": r["created_at"],
                "messages": messages,
            })
        return conversations

    def load_messages(self, conversation_id: str) -> list[dict[str, Any]]:
        """Load messages and linked analyses for a conversation."""
        self._require_supabase()
        # Always refresh from Supabase; SQLite is only a local cache.
        if self.supabase:
            try:
                res = self.supabase.table("messages").select("*").eq("conversation_id", conversation_id).order("created_at", desc=False).execute()
                if res and res.data:
                    with self._connection() as conn:
                        for m in res.data:
                            conn.execute(
                                """
                                INSERT INTO local_messages (id, conversation_id, role, content, has_image, created_at)
                                VALUES (?, ?, ?, ?, ?, ?)
                                ON CONFLICT(id) DO NOTHING
                                """,
                                (m.get("id"), m.get("conversation_id"), m.get("role"), m.get("content") or "", int(bool(m.get("has_image"))), m.get("created_at") or datetime.now().isoformat()),
                            )
                    message_ids = [m.get("id") for m in res.data if m.get("id")]
                    if message_ids:
                        analyses_res = self.supabase.table("analyses").select("*").in_("message_id", message_ids).execute()
                        with self._connection() as conn:
                            for item in (analyses_res.data or []):
                                conn.execute(
                                    "INSERT OR IGNORE INTO local_analyses (id, message_id, predicted_class, confidence, probabilities, model_version, is_cheese, message, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                    (
                                        str(uuid4()), item["message_id"], item.get("predicted_class") or "inconnu",
                                        float(item.get("confidence") or 0), json.dumps(item.get("probabilities") or {}),
                                        item.get("model_version") or "1.0", int(bool(item.get("is_cheese", True))),
                                        item.get("message"), item.get("created_at") or datetime.now().isoformat(),
                                    ),
                                )
            except Exception as exc:
                raise RuntimeError("Impossible de lire les messages dans Supabase.") from exc

        # 2. Return all local messages with analyses
        with self._connection() as conn:
            conn.row_factory = sqlite3.Row
            m_rows = conn.execute(
                "SELECT id, role, content, has_image, created_at FROM local_messages WHERE conversation_id = ? ORDER BY created_at ASC",
                (conversation_id,),
            ).fetchall()

            messages = []
            for m in m_rows:
                msg_id = m["id"]
                analysis = None
                a_row = conn.execute(
                    "SELECT predicted_class, confidence, probabilities, model_version, is_cheese, message FROM local_analyses WHERE message_id = ?",
                    (msg_id,),
                ).fetchone()
                if a_row:
                    try:
                        probs = json.loads(a_row["probabilities"])
                    except Exception:
                        probs = {}
                    analysis = {
                        "is_cheese": bool(a_row["is_cheese"]),
                        "predicted_class": a_row["predicted_class"],
                        "confidence": a_row["confidence"],
                        "probabilities": probs,
                        "model_version": a_row["model_version"],
                        "message": a_row["message"],
                    }

                messages.append({
                    "id": msg_id,
                    "role": m["role"],
                    "content": m["content"],
                    "has_image": bool(m["has_image"]),
                    "analysis": analysis,
                    "created_at": m["created_at"],
                })

        return messages

    def create_conversation(self, user_id: str, title: str = "Nouvelle discussion") -> dict[str, Any]:
        """Create a new conversation locally and sync with Supabase."""
        conv_id = str(uuid4())
        now = self._utc_now().isoformat()
        self._require_supabase()
        try:
            self.supabase.table("conversations").insert({
                "id": conv_id,
                "user_id": user_id,
                "title": title,
            }).execute()
            with self._connection() as conn:
                conn.execute(
                    "INSERT INTO local_conversations (id, user_id, title, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    (conv_id, user_id, title, now, now),
                )
        except Exception as exc:
            raise RuntimeError("Impossible de créer la conversation dans Supabase. Vérifiez les droits et les tables.") from exc

        return {"id": conv_id, "title": title, "messages": [], "created_at": now}

    def update_conversation_title(self, conversation_id: str, title: str) -> None:
        """Update conversation title."""
        title = title.strip()[:60]
        now = self._utc_now().isoformat()
        self._require_supabase()
        try:
            self.supabase.table("conversations").update({"title": title}).eq("id", conversation_id).execute()
            if self._has_updated_at():
                self.supabase.table("conversations").update({"updated_at": now}).eq("id", conversation_id).execute()
            with self._connection() as conn:
                conn.execute(
                    "UPDATE local_conversations SET title = ?, updated_at = ? WHERE id = ?",
                    (title, now, conversation_id),
                )
        except Exception as exc:
            raise RuntimeError("Impossible de modifier le titre dans Supabase.") from exc

    def delete_conversation(self, user_id: str, conversation_id: str) -> None:
        """Delete a conversation and all its messages."""
        self._require_supabase()
        try:
            owned = (
                self.supabase.table("conversations")
                .select("id")
                .eq("id", conversation_id)
                .eq("user_id", user_id)
                .limit(1)
                .execute()
            )
            if owned.data:
                message_rows = (
                    self.supabase.table("messages")
                    .select("id")
                    .eq("conversation_id", conversation_id)
                    .execute()
                )
                message_ids = [row["id"] for row in (message_rows.data or []) if row.get("id")]
                if message_ids:
                    self.supabase.table("analyses").delete().in_("message_id", message_ids).execute()
                self.supabase.table("messages").delete().eq("conversation_id", conversation_id).execute()
                self.supabase.table("conversations").delete().eq("id", conversation_id).eq("user_id", user_id).execute()
            with self._connection() as conn:
                conn.execute("DELETE FROM local_analyses WHERE message_id IN (SELECT id FROM local_messages WHERE conversation_id = ?)", (conversation_id,))
                conn.execute("DELETE FROM local_messages WHERE conversation_id = ?", (conversation_id,))
                conn.execute("DELETE FROM local_conversations WHERE id = ? AND user_id = ?", (conversation_id, user_id))
        except Exception as exc:
            raise RuntimeError("Impossible de supprimer la conversation dans Supabase.") from exc

    def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        image=None,
        analysis: dict | None = None,
    ) -> str:
        """Persist a message and optional analysis to SQLite and Supabase."""
        msg_id = str(uuid4())
        has_image = 1 if image is not None else 0
        now = self._utc_now().isoformat()

        self._require_supabase()
        analysis_id = str(uuid4()) if analysis else None
        probs_json = json.dumps(analysis.get("probabilities", {})) if analysis else None
        pred_class = (analysis.get("predicted_class") or "inconnu") if analysis else None
        conf = float(analysis.get("confidence") or 0.0) if analysis else None
        model_ver = str(analysis.get("model_version") or "1.0") if analysis else None

        try:
            self.supabase.table("messages").insert({
                "id": msg_id,
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
            }).execute()
            if analysis:
                self.supabase.table("analyses").insert({
                    "message_id": msg_id,
                    "predicted_class": pred_class,
                    "confidence": conf,
                    "probabilities": analysis.get("probabilities", {}),
                    "model_version": model_ver,
                }).execute()
            if self._has_updated_at():
                self.supabase.table("conversations").update({"updated_at": now}).eq("id", conversation_id).execute()
            with self._connection() as conn:
                conn.execute(
                    "INSERT INTO local_messages (id, conversation_id, role, content, has_image, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (msg_id, conversation_id, role, content, has_image, now),
                )
                conn.execute("UPDATE local_conversations SET updated_at = ? WHERE id = ?", (now, conversation_id))
                if analysis:
                    conn.execute(
                        "INSERT INTO local_analyses (id, message_id, predicted_class, confidence, probabilities, model_version, is_cheese, message, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (analysis_id, msg_id, pred_class, conf, probs_json, model_ver, int(bool(analysis.get("is_cheese", True))), analysis.get("message"), now),
                    )
        except Exception as exc:
            # Avoid leaving a remote message without its required analysis.
            try:
                self.supabase.table("messages").delete().eq("id", msg_id).execute()
            except Exception:
                pass
            raise RuntimeError("Impossible d’enregistrer le message ou son analyse dans Supabase.") from exc

        return msg_id
