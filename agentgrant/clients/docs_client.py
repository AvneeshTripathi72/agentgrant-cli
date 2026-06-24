from __future__ import annotations

from difflib import SequenceMatcher

from agentgrant.core.cache_manager import CacheManager
from agentgrant.core.constants import DEFAULT_DOCS_CACHE_TTL
from agentgrant.core.session import HTTPSession
from agentgrant.models.docs import DocsPage, DocsSearchResult
from agentgrant.utils.parser import parse_llms_text


class DocsClient:
    def __init__(
        self, base_url: str, cache: CacheManager | None = None, use_cache: bool = True
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.cache = cache
        self.use_cache = use_cache

    async def fetch_pages(self) -> list[DocsPage]:
        cache_key = "llms"
        if self.cache and self.use_cache:
            cached = self.cache.read("docs", cache_key, ttl_seconds=DEFAULT_DOCS_CACHE_TTL)
            if cached is not None:
                return [DocsPage.model_validate(item) for item in cached]

        async with HTTPSession() as session:
            response = await session.request("GET", f"{self.base_url}/llms.txt")
            pages = parse_llms_text(response.text, self.base_url)
        if self.cache and self.use_cache:
            self.cache.write("docs", cache_key, [page.model_dump(mode="json") for page in pages])
        return pages

    async def fetch_page_content(self, page: DocsPage) -> str:
        cache_key = f"page:{page.slug}"
        if self.cache and self.use_cache:
            cached = self.cache.read("docs-pages", cache_key, ttl_seconds=DEFAULT_DOCS_CACHE_TTL)
            if isinstance(cached, str):
                return cached
        async with HTTPSession() as session:
            response = await session.request("GET", str(page.url))
            content = response.text
        if self.cache and self.use_cache:
            self.cache.write("docs-pages", cache_key, content)
        return content

    async def search(self, query: str) -> list[DocsSearchResult]:
        pages = await self.fetch_pages()
        lowered = query.casefold()
        results: list[DocsSearchResult] = []
        for page in pages:
            title_score = SequenceMatcher(None, lowered, page.title.casefold()).ratio()
            slug_score = SequenceMatcher(None, lowered, page.slug.casefold()).ratio()
            content = await self.fetch_page_content(page)
            count_score = content.casefold().count(lowered) + (
                page.description or ""
            ).casefold().count(lowered)
            score = title_score * 3 + slug_score * 2 + count_score
            if score <= 0 and lowered not in content.casefold():
                continue
            snippet = next(
                (line.strip() for line in content.splitlines() if lowered in line.casefold()),
                page.title,
            )
            results.append(DocsSearchResult(page=page, score=score, snippet=snippet))
        return sorted(results, key=lambda item: item.score, reverse=True)

    async def resolve_page(self, name: str) -> DocsPage:
        pages = await self.fetch_pages()
        lowered = name.casefold()
        exact = next(
            (page for page in pages if page.slug == lowered or page.title.casefold() == lowered),
            None,
        )
        if exact:
            return exact
        fuzzy = sorted(
            pages,
            key=lambda page: max(
                SequenceMatcher(None, lowered, page.slug.casefold()).ratio(),
                SequenceMatcher(None, lowered, page.title.casefold()).ratio(),
            ),
            reverse=True,
        )
        return fuzzy[0]
