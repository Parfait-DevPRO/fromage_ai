"""Application settings loaded from Streamlit secrets or environment variables."""
from __future__ import annotations

import os
import tomllib
from pathlib import Path
try:  # Allows pure unit tests to run before the Streamlit dependency is installed.
    import streamlit as st
except ModuleNotFoundError:
    st = None

BASE_DIR = Path(__file__).resolve().parent.parent
ML_DIR = BASE_DIR / "ml"


def resolve_model_path() -> Path:
    """Use the conventional filename or the single model supplied in ml/."""
    conventional = ML_DIR / "cheese_model.keras"
    if conventional.exists():
        return conventional
    candidates = sorted((*ML_DIR.glob("*.keras"), *ML_DIR.glob("*.h5")))
    return candidates[0] if len(candidates) == 1 else conventional


MODEL_PATH = resolve_model_path()
LABELS_PATH = BASE_DIR / "ml" / "labels.json"
PROMPT_PATH = BASE_DIR / "prompts" / "cheese_expert_prompt.txt"
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


def secret(name: str, default: str = "") -> str:
    """Read a root-level secret without validating its format or exposing it."""
    if st is not None:
        try:
            value = st.secrets.get(name)
            if value is not None and str(value).strip():
                return str(value).strip()
        except Exception:
            pass
    value = os.getenv(name)
    if value and value.strip():
        return value.strip()
    # Fallback for local executions where Streamlit's secrets manager was not initialised.
    secrets_path = BASE_DIR / ".streamlit" / "secrets.toml"
    try:
        value = tomllib.loads(secrets_path.read_text(encoding="utf-8")).get(name)
        if value is not None and str(value).strip():
            return str(value).strip()
    except (FileNotFoundError, tomllib.TOMLDecodeError, OSError):
        pass
    return default
