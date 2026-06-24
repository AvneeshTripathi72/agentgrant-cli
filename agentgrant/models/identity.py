from __future__ import annotations

from pydantic import BaseModel, Field


class Identity(BaseModel):
    id: str
    name: str | None = None
    email: str | None = None
    type: str | None = None
    attributes: dict[str, str] = Field(default_factory=dict)


class IdentityListResponse(BaseModel):
    items: list[Identity] = Field(default_factory=list)
