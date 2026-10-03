"""Supabase persistence adapter. The UI remains usable locally when it is not configured."""
from __future__ import annotations
from config.settings import secret


class StorageService:
    def __init__(self):
        self.client = None
        url, key = secret("SUPABASE_URL"), secret("SUPABASE_KEY")
        if url and key:
            try:
                from supabase import create_client
                self.client = create_client(url, key)
            except Exception:
                self.client = None

    def save_message(self, conversation_id: str, role: str, content: str, analysis: dict | None = None) -> None:
        if not self.client:
            return
        message = self.client.table("messages").insert({"conversation_id": conversation_id, "role": role, "content": content}).execute().data
        if analysis and message:
            self.client.table("analyses").insert({"message_id": message[0]["id"], **analysis}).execute()
