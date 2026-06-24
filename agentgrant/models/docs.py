from __future__ import annotations

from pydantic import BaseModel, HttpUrl


class DocsPage(BaseModel):
    title: str
    slug: str
    url: HttpUrl
    description: str | None = None
    content: str | None = None


class DocsSearchResult(BaseModel):
    page: DocsPage
    score: float
    snippet: str
