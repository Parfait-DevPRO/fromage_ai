from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Conversation:
    id: str
    title: str
    user_id: str | None = None
    created_at: datetime | None = None
