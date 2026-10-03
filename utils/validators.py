from __future__ import annotations
from config.settings import MAX_UPLOAD_BYTES


def validate_upload(uploaded_file) -> None:
    if uploaded_file is None:
        return
    if uploaded_file.size > MAX_UPLOAD_BYTES:
        raise ValueError("L'image dépasse la taille maximale autorisée (10 Mo).")
    if not (uploaded_file.type or "").startswith("image/"):
        raise ValueError("Veuillez sélectionner une image JPG, PNG ou WEBP.")
