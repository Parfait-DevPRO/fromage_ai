from __future__ import annotations
from io import BytesIO
from PIL import Image, UnidentifiedImageError


def open_image(data: bytes) -> Image.Image:
    try:
        image = Image.open(BytesIO(data))
        image.verify()
        return Image.open(BytesIO(data)).convert("RGB")
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("Le fichier envoyé n'est pas une image valide.") from exc
