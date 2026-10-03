"""Unified Database Service for local SQLite and Supabase Cloud synchronization.

Ensures the application works instantly offline/locally, while continuously syncing
conversations, messages, and cheese analyses to Supabase when connected.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from typing import Any

from config.settings import BASE_DIR
from config.supabase_client import get_supabase_client

DATABASE_PATH = BASE_DIR / "data" / "cheese_ai.db"


class DatabaseService:
    def __init__(self, db_path: Path = DATABASE_PATH, supabase_client=None):
        self.db_path = Path(db_path)
        self.supabase = supabase_client if supabase_client is not None else get_supabase_client()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_sqlite()

    def _connection(self):
        return sqlite3.connect(self.db_path)

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
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """)

    def load_conversations(self, user_id: str) -> list[dict[str, Any]]:
        """Load all conversations for a user. Syncs with Supabase if reachable."""
        # 1. First attempt to pull conversations from Supabase if connected
        if self.supabase:
            try:
                res = self.supabase.table("conversations").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
                if res and res.data:
                    with self._connection() as conn:
                        for row in res.data:
                            conn.execute(
                                """
                                INSERT INTO local_conversations (id, user_id, title, created_at, updated_at)
                                VALUES (?, ?, ?, ?, ?)
                                ON CONFLICT(id) DO UPDATE SET title = excluded.title
                                """,
                                (
                                    row.get("id"),
                                    row.get("user_id"),
                                    row.get("title") or "Discussion",
                                    row.get("created_at") or datetime.now().isoformat(),
                                    row.get("updated_at") or datetime.now().isoformat(),
                                ),
                            )
            except Exception:
                pass

        # 2. Return from local database (guaranteed fast and reliable)
        with self._connection() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT id, user_id, title, created_at, updated_at FROM local_conversations WHERE user_id = ? ORDER BY created_at DESC",
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
        # 1. Attempt to pull from Supabase if empty locally
        with self._connection() as conn:
            conn.row_factory = sqlite3.Row
            count = conn.execute("SELECT COUNT(*) as c FROM local_messages WHERE conversation_id = ?", (conversation_id,)).fetchone()["c"]

        if count == 0 and self.supabase:
            try:
                res = self.supabase.table("messages").select("*").eq("conversation_id", conversation_id).order("created_at", desc=False).execute()
                if res and res.data:
                    with self._connection() as conn:
                        for m in res.data:
                            conn.execute(
                                """
                                INSERT INTO local_messages (id, conversation_id, role, content, has_image, created_at)
                                VALUES (?, ?, ?, ?, 0, ?)
                                ON CONFLICT(id) DO NOTHING
                                """,
                                (m.get("id"), m.get("conversation_id"), m.get("role"), m.get("content") or "", m.get("created_at")),
                            )
            except Exception:
                pass

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
                    "SELECT predicted_class, confidence, probabilities, model_version FROM local_analyses WHERE message_id = ?",
                    (msg_id,),
                ).fetchone()
                if a_row:
                    try:
                        probs = json.loads(a_row["probabilities"])
                    except Exception:
                        probs = {}
                    analysis = {
                        "is_cheese": True,
                        "predicted_class": a_row["predicted_class"],
                        "confidence": a_row["confidence"],
                        "probabilities": probs,
                        "model_version": a_row["model_version"],
                    }

                messages.append({
                    "id": msg_id,
                    "role": m["role"],
                    "content": m["content"],
                    "analysis": analysis,
                    "created_at": m["created_at"],
                })

        return messages

    def create_conversation(self, user_id: str, title: str = "Nouvelle discussion") -> dict[str, Any]:
        """Create a new conversation locally and sync with Supabase."""
        conv_id = str(uuid4())
        now = datetime.now().isoformat()
        with self._connection() as conn:
            conn.execute(
                "INSERT INTO local_conversations (id, user_id, title, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (conv_id, user_id, title, now, now),
            )

        if self.supabase:
            try:
                self.supabase.table("conversations").insert({
                    "id": conv_id,
                    "user_id": user_id,
                    "title": title,
                }).execute()
            except Exception:
                pass

        return {"id": conv_id, "title": title, "messages": [], "created_at": now}

    def update_conversation_title(self, conversation_id: str, title: str) -> None:
        """Update conversation title."""
        title = title.strip()[:60]
        now = datetime.now().isoformat()
        with self._connection() as conn:
            conn.execute(
                "UPDATE local_conversations SET title = ?, updated_at = ? WHERE id = ?",
                (title, now, conversation_id),
            )
        if self.supabase:
            try:
                self.supabase.table("conversations").update({"title": title}).eq("id", conversation_id).execute()
            except Exception:
                pass

    def delete_conversation(self, conversation_id: str) -> None:
        """Delete a conversation and all its messages."""
        with self._connection() as conn:
            conn.execute("DELETE FROM local_messages WHERE conversation_id = ?", (conversation_id,))
            conn.execute("DELETE FROM local_conversations WHERE id = ?", (conversation_id,))

        if self.supabase:
            try:
                self.supabase.table("conversations").delete().eq("id", conversation_id).execute()
            except Exception:
                pass

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
        now = datetime.now().isoformat()

        # 1. Local SQLite storage
        with self._connection() as conn:
            conn.execute(
                "INSERT INTO local_messages (id, conversation_id, role, content, has_image, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (msg_id, conversation_id, role, content, has_image, now),
            )
            if analysis:
                analysis_id = str(uuid4())
                probs_json = json.dumps(analysis.get("probabilities", {}))
                pred_class = analysis.get("predicted_class") or "inconnu"
                conf = float(analysis.get("confidence") or 0.0)
                model_ver = str(analysis.get("model_version") or "1.0")
                conn.execute(
                    """
                    INSERT INTO local_analyses (id, message_id, predicted_class, confidence, probabilities, model_version, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (analysis_id, msg_id, pred_class, conf, probs_json, model_ver, now),
                )

        # 2. Remote Supabase storage
        if self.supabase:
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
            except Exception:
                pass

        return msg_id
