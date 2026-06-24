from __future__ import annotations

from pydantic import BaseModel, HttpUrl


class DocPage(BaseModel):
    title: str
    url: HttpUrl
    slug: str
    description: str | None = None


class SearchResult(BaseModel):
    page: DocPage
    score: int
    snippet: str

