from __future__ import annotations

from config.settings import PROMPT_PATH, secret
from services.api_usage_service import record_request


class GeminiService:
    def __init__(self, api_key: str | None = None, model_name: str | None = None):
        self.api_key = api_key or secret("GEMINI_API_KEY")
        self.model_name = model_name or secret("GEMINI_MODEL", "gemini-3.6-flash")

    @staticmethod
    def analysis_context(analysis_result: dict | None) -> str:
        if not analysis_result:
            return "Aucun résultat d'analyse d'image n'a été fourni."
        predicted_class = analysis_result.get("predicted_class")
        if not analysis_result.get("is_cheese"):
            return "L'image ne semble pas représenter un fromage. Refuse poliment l'analyse."

        confidence = analysis_result.get("confidence")
        if confidence is None:
            confidence = analysis_result.get("confidence_text", "non disponible")
        else:
            confidence = f"{float(confidence):.2f}"
        return (
            "Donnée interne à présenter sans citer sa source : analyse visuelle = "
            f"« {predicted_class} » ; pourcentage = {confidence} %. "
            "Annonce exactement cette classe et ce pourcentage, puis explique-les avec tact. "
            "Ne mentionne jamais API, IA, Gemini, Keras ou modèle."
        )

    def generate_response(self, user_message: str, analysis_result=None, image=None, conversation_history=None) -> str:
        if not self.api_key:
            return "Le service de réponse est indisponible pour le moment. Réessayez dans quelques instants."
        try:
            from google import genai

            system = PROMPT_PATH.read_text(encoding="utf-8")
            history = "\n".join(f"{m['role']}: {m['content']}" for m in (conversation_history or [])[-10:])
            prompt = f"{system}\n\n{self.analysis_context(analysis_result)}\n\nHistorique:\n{history}\n\nUtilisateur: {user_message}"
            client = genai.Client(api_key=self.api_key)
            contents = [prompt, image] if image is not None else prompt
            try:
                record_request()
                response = client.models.generate_content(model=self.model_name, contents=contents)
            except Exception as exc:
                if getattr(exc, "code", None) == 404 and self.model_name == "gemini-2.0-flash":
                    self.model_name = "gemini-3.6-flash"
                    record_request()
                    response = client.models.generate_content(model=self.model_name, contents=contents)
                else:
                    raise
            return response.text or "Je n'ai pas pu générer de réponse."
        except Exception as exc:
            status = getattr(exc, "code", None)
            if status in (401, 403):
                return "Le service de réponse est indisponible pour le moment. Réessayez dans quelques instants."
            if status == 429:
                return "Votre limite de discussion a été atteinte. Réessayez plus tard."
            if status == 404:
                return "Le service de réponse est indisponible pour le moment. Réessayez dans quelques instants."
            return "Le service de réponse est indisponible pour le moment. Réessayez dans quelques instants."
