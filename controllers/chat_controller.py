from __future__ import annotations
from services.gemini_service import GeminiService
from services.storage_service import StorageService


class ChatController:
    def __init__(self):
        self.gemini = GeminiService()
        self.storage = StorageService()

    def reply(self, text: str, analysis=None, image=None, history=None) -> str:
        return self.gemini.generate_response(text, analysis, image=image, conversation_history=history)
