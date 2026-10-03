from __future__ import annotations

from config.settings import LABELS_PATH, MODEL_PATH
from services.keras_service import KerasService
from utils.image_utils import open_image
from utils.validators import validate_upload


class AnalysisController:
    def __init__(self, service=None):
        self.service = service or KerasService(MODEL_PATH, LABELS_PATH)

    def analyze_upload(self, uploaded_file):
        validate_upload(uploaded_file)
        image = open_image(uploaded_file.getvalue())
        return self.service.analyze_image(image), image
