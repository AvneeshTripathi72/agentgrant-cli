from __future__ import annotations

from pydantic import BaseModel


class Scope(BaseModel):
    name: str
    description: str | None = None
