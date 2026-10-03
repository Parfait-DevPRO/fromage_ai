from __future__ import annotations
from dataclasses import dataclass


@dataclass
class User:
    id: str
    email: str | None = None
    display_name: str | None = None
