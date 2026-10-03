from __future__ import annotations

import base64
from functools import lru_cache
from pathlib import Path

ICON_PATH = Path(__file__).resolve().parents[1] / "assets" / "cheese_icon.svg"


@lru_cache(maxsize=1)
def icon_data_uri() -> str:
    encoded = base64.b64encode(ICON_PATH.read_bytes()).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def icon_html(size: int = 24) -> str:
    return (
        f'<img src="{icon_data_uri()}" width="{size}" height="{size}" '
        'style="vertical-align:middle;object-fit:contain" alt="" />'
    )
