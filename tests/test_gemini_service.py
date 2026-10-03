from services.gemini_service import GeminiService


def test_analysis_context_exposes_prediction_and_score():
    context = GeminiService.analysis_context({
        "is_cheese": True,
        "predicted_class": "moisissure",
        "confidence": 91.37,
    })
    assert "moisissure" in context
    assert "91.37" in context
    assert "%" in context
