"""Default preprocessing. Adapt this file once your Keras model's requirements are known."""
from __future__ import annotations
import numpy as np


def preprocess_image(image, target_size: tuple[int, int]) -> np.ndarray:
    """Match the training notebook: RGB pixels are kept in the [0, 255] range.

    The saved model already includes its ResNetV2 Rescaling layer, so scaling here
    would normalise the image twice and distort predictions.
    """
    resized = image.resize(target_size)
    values = np.asarray(resized, dtype=np.float32)
    return np.expand_dims(values, axis=0)
