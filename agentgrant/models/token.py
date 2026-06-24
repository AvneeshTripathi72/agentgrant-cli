from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TokenPayload(BaseModel):
    header: dict[str, Any] = Field(default_factory=dict)
    claims: dict[str, Any] = Field(default_factory=dict)
    valid: bool | None = None
    algorithm: str | None = None
