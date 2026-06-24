from __future__ import annotations

import asyncio
import re
from urllib.parse import urljoin, urlparse

import click

from agentgrant.models import DocPage, SearchResult
from agentgrant.utils.http_client import AgentGrantClient
from agentgrant.utils.printer import Printer


LINK_PATTERN = re.compile(r"^\s*(?:[-*]\s+)?\[([^\]]+)\]\(([^)]+)\)(?:\s*-\s*(.+))?\s*$")
URL_PATTERN = re.compile(r"^\s*(https?://\S+)\s*$")


def parse_llms_text(llms_text: str, docs_base_url: str) -> list[DocPage]:
    pages: list[DocPage] = []
    seen: set[str] = set()

    for raw_line in llms_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        title: str | None = None
        href: str | None = None
        description: str | None = None

        if match := LINK_PATTERN.match(line):
            title, href, description = match.groups()
        elif match := URL_PATTERN.match(line):
            href = match.group(1)
            parsed = urlparse(href)
            title = parsed.path.rstrip("/").split("/")[-1] or parsed.netloc

        if not href or not title:
            continue

        absolute_url = urljoin(docs_base_url.rstrip("/") + "/", href)
        slug = urlparse(absolute_url).path.rstrip("/").split("/")[-1] or title.lower().replace(" ", "-")
        if absolute_url in seen:
            continue
        seen.add(absolute_url)
        pages.append(DocPage(title=title, url=absolute_url, slug=slug, description=description))

    return pages


async def fetch_doc_pages(client: AgentGrantClient) -> list[DocPage]:
    llms_url = f"{client.settings.docs_base_url.rstrip('/')}/llms.txt"
    llms_text = await client.fetch_text(llms_url)
    return parse_llms_text(llms_text, client.settings.docs_base_url)


async def search_docs(client: AgentGrantClient, query: str) -> list[SearchResult]:
    pages = await fetch_doc_pages(client)
    lowered_query = query.casefold()
    semaphore = asyncio.Semaphore(8)

    async def evaluate(page: DocPage) -> SearchResult | None:
        async with semaphore:
            body = await client.fetch_text(str(page.url))
        haystack = "\n".join([page.title, page.description or "", body])
        if lowered_query not in haystack.casefold():
            return None
        score = haystack.casefold().count(lowered_query)
        snippet = first_matching_line(body, lowered_query) or page.description or page.title
        return SearchResult(page=page, score=score, snippet=snippet)

    results = await asyncio.gather(*[evaluate(page) for page in pages])
    ranked = [result for result in results if result is not None]
    return sorted(ranked, key=lambda item: item.score, reverse=True)


def first_matching_line(content: str, lowered_query: str) -> str:
    for line in content.splitlines():
        if lowered_query in line.casefold():
            return line.strip()
    return ""


async def render_docs(client: AgentGrantClient, printer: Printer) -> None:
    pages = await fetch_doc_pages(client)
    if printer.json_output:
        printer.print_json([page.model_dump(mode="json") for page in pages])
        return
    printer.print_table(
        "Documentation Pages",
        ["title", "slug", "url", "description"],
        [[page.title, page.slug, str(page.url), page.description or ""] for page in pages],
    )


async def render_search(client: AgentGrantClient, printer: Printer, query: str) -> None:
    results = await search_docs(client, query)
    if printer.json_output:
        printer.print_json(
            [
                {
                    "page": result.page.model_dump(mode="json"),
                    "score": result.score,
                    "snippet": result.snippet,
                }
                for result in results
            ]
        )
        return
    printer.print_table(
        f"Results for '{query}'",
        ["title", "slug", "score", "snippet"],
        [[result.page.title, result.page.slug, result.score, result.snippet] for result in results],
    )


async def render_page(client: AgentGrantClient, printer: Printer, page_name: str) -> None:
    pages = await fetch_doc_pages(client)
    selected = next(
        (
            page
            for page in pages
            if page.slug == page_name or page.title.casefold() == page_name.casefold() or page_name.casefold() in page.slug
        ),
        None,
    )
    if selected is None:
        raise click.ClickException(f"Documentation page '{page_name}' was not found.")

    body = await client.fetch_text(str(selected.url))
    if printer.json_output:
        printer.print_json({"page": selected.model_dump(mode="json"), "content": body})
        return
    printer.print_message(f"# {selected.title}", style="bold cyan")
    printer.print_markdown(body)

