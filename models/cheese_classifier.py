"""Protocols and output contract for cheese classifiers."""
from typing import Protocol
from models.analysis import Analysis


class CheeseClassifier(Protocol):
    def analyze_image(self, image) -> Analysis: ...
