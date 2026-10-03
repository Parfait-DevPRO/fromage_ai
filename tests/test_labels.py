import json
from config.settings import LABELS_PATH


def test_model_labels_match_the_four_output_classes():
    labels = json.loads(LABELS_PATH.read_text(encoding="utf-8"))
    assert labels == ["fromage dessechement", "fromage fissure", "fromage moissure", "fromage sain"]
