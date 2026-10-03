"""Keras inference: the only source of classification scores in Fromazy_AI."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from models.analysis import Analysis
from ml.preprocessing import preprocess_image


class KerasService:
    def __init__(self, model_path: Path, labels_path: Path, model=None):
        self.model_path = Path(model_path)
        self.labels_path = Path(labels_path)
        self._model = model
        self.labels = self._load_labels()

    def _load_labels(self) -> list[str]:
        if not self.labels_path.exists():
            return []
        labels = json.loads(self.labels_path.read_text(encoding="utf-8"))
        if not isinstance(labels, list) or not all(isinstance(x, str) for x in labels):
            raise ValueError("ml/labels.json doit contenir une liste de noms de classes.")
        return labels

    def _get_model(self):
        if self._model is not None:
            return self._model
        if not self.model_path.exists():
            raise FileNotFoundError("Modèle Keras absent : placez-le dans ml/cheese_model.keras.")
        try:
            import tensorflow as tf
            self._model = tf.keras.models.load_model(self.model_path)
            return self._model
        except Exception as exc:
            raise RuntimeError("Impossible de charger le modèle Keras. Vérifiez TensorFlow et le fichier modèle.") from exc

    @staticmethod
    def scores_to_percentages(scores) -> list[float]:
        """Convert probabilities in [0,1] once; leave percentage outputs unchanged."""
        values = np.asarray(scores, dtype=float).flatten()
        if values.size == 0 or not np.all(np.isfinite(values)):
            raise ValueError("La sortie du modèle est vide ou invalide.")
        if np.min(values) >= 0 and np.max(values) <= 1.00001:
            values = values * 100
        return [float(x) for x in values]

    @staticmethod
    def score_text(score: float) -> str:
        return str(float(score))

    def analyze_image(self, image) -> Analysis:
        model = self._get_model()
        if not self.labels:
            raise ValueError("Les labels du modèle sont absents. Renseignez ml/labels.json.")
        input_shape = getattr(model, "input_shape", None)
        if not input_shape or len(input_shape) < 3 or input_shape[1] is None or input_shape[2] is None:
            raise ValueError("La taille d'entrée du modèle est indéterminée. Configurez son preprocessing.")
        raw = model.predict(preprocess_image(image, (int(input_shape[2]), int(input_shape[1]))), verbose=0)
        values = self.scores_to_percentages(raw)
        if len(values) != len(self.labels):
            raise ValueError("Le nombre de scores Keras ne correspond pas au nombre de labels.")
        probabilities = dict(zip(self.labels, values))
        predicted_class = max(probabilities, key=probabilities.get)
        probability_text = {label: self.score_text(score) for label, score in probabilities.items()}
        return Analysis(True, predicted_class, probabilities[predicted_class], probabilities, "1.0",
                        probabilities_text=probability_text,
                        confidence_text=probability_text[predicted_class])
