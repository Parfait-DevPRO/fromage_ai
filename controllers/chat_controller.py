from __future__ import annotations
from services.gemini_service import GeminiService


class ChatController:
    def __init__(self):
        self.gemini = GeminiService()

    def reply(self, text: str, analysis=None, image=None, history=None) -> str:
        return self.gemini.generate_response(text, analysis, image=image, conversation_history=history)
