from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class Analysis:
    is_cheese: bool
    predicted_class: str | None
    confidence: float | None
    probabilities: dict[str, float]
    model_version: str
    message: str | None = None
    probabilities_text: dict[str, str] | None = None
    confidence_text: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
