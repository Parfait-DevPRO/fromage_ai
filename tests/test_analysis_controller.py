from io import BytesIO

from PIL import Image

from controllers.analysis_controller import AnalysisController
from models.analysis import Analysis


class Upload:
    type = "image/png"
    size = 100

    @staticmethod
    def getvalue():
        buffer = BytesIO()
        Image.new("RGB", (2, 2), "white").save(buffer, format="PNG")
        return buffer.getvalue()


class KerasSpy:
    def __init__(self):
        self.called = False

    def analyze_image(self, image):
        self.called = True
        return Analysis(True, "fromage sain", 99.0, {}, "1.0")


def test_every_valid_image_is_sent_to_keras_without_a_cheese_gate():
    keras = KerasSpy()
    result, _ = AnalysisController(service=keras).analyze_upload(Upload())

    assert keras.called is True
    assert result.predicted_class == "fromage sain"
