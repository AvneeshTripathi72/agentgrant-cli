from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse

from pydantic import HttpUrl, TypeAdapter

from agentgrant.models.docs import DocsPage

LINK_PATTERN = re.compile(r"^\s*(?:[-*]\s+)?\[([^\]]+)\]\(([^)]+)\)(?:\s*-\s*(.+))?\s*$")
URL_PATTERN = re.compile(r"^\s*(https?://\S+)\s*$")
HTTP_URL_ADAPTER = TypeAdapter(HttpUrl)


def parse_llms_text(llms_text: str, docs_base_url: str) -> list[DocsPage]:
    pages: list[DocsPage] = []
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
        if not title or not href:
            continue
        absolute_url = urljoin(docs_base_url.rstrip("/") + "/", href)
        slug = urlparse(absolute_url).path.rstrip("/").split("/")[-1] or title.casefold().replace(
            " ", "-"
        )
        validated_url = HTTP_URL_ADAPTER.validate_python(absolute_url)
        if absolute_url in seen:
            continue
        seen.add(absolute_url)
        pages.append(DocsPage(title=title, slug=slug, url=validated_url, description=description))
    return pages
