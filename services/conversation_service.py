from __future__ import annotations
from uuid import uuid4


class ConversationService:
    @staticmethod
    def new_conversation() -> dict:
        return {"id": str(uuid4()), "title": "Nouvelle conversation", "messages": []}

    @staticmethod
    def title_from(text: str) -> str:
        return (text.strip() or "Analyse de fromage")[:42]
