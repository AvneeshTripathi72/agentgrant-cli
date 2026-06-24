from __future__ import annotations

from pydantic import BaseModel, Field


class Grant(BaseModel):
    id: str
    subject: str = ""
    scope: str = ""
    status: str = ""
    expires_at: str | None = None


class GrantListResponse(BaseModel):
    items: list[Grant] = Field(default_factory=list)
    page: int = 1
    limit: int = 20
    total: int = 0
