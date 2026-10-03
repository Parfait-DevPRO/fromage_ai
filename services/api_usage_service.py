"""Local estimate of daily Gemini requests made by this application."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from config.settings import BASE_DIR

USAGE_FILE = BASE_DIR / "data" / "gemini_usage.json"


def today_count() -> int:
    try:
        data = json.loads(USAGE_FILE.read_text(encoding="utf-8"))
        return int(data.get(date.today().isoformat(), 0))
    except (FileNotFoundError, json.JSONDecodeError, OSError, TypeError, ValueError):
        return 0


def record_request() -> None:
    USAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        data = json.loads(USAGE_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        data = {}
    data = {date.today().isoformat(): int(data.get(date.today().isoformat(), 0)) + 1}
    USAGE_FILE.write_text(json.dumps(data), encoding="utf-8")
