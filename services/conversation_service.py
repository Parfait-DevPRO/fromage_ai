from __future__ import annotations

from services.database_service import DatabaseService


class ConversationService:
    _database = None

    @classmethod
    def database(cls) -> DatabaseService:
        if cls._database is None:
            cls._database = DatabaseService()
        return cls._database

    @staticmethod
    def new_conversation(user_id: str) -> dict:
        return ConversationService.database().create_conversation(user_id)

    @staticmethod
    def load_for_user(user_id: str) -> list[dict]:
        conversations = ConversationService.database().load_conversations(user_id)
        return conversations or [ConversationService.new_conversation(user_id)]

    @staticmethod
    def purge_expired(user_id: str, retention_days: int = 3) -> set[str]:
        return ConversationService.database().purge_expired_conversations(user_id, retention_days)

    @staticmethod
    def save_message(conversation_id: str, role: str, content: str, image=None, analysis=None) -> str:
        return ConversationService.database().save_message(
            conversation_id, role, content, image=image, analysis=analysis
        )

    @staticmethod
    def rename(conversation_id: str, title: str) -> None:
        ConversationService.database().update_conversation_title(conversation_id, title)

    @staticmethod
    def delete(user_id: str, conversation_id: str) -> None:
        ConversationService.database().delete_conversation(user_id, conversation_id)

    @staticmethod
    def title_from(text: str) -> str:
        return (text.strip() or "Analyse de fromage")[:42]
