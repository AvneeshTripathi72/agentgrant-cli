from __future__ import annotations

import click

from agentgrant.clients.docs_client import DocsClient
from agentgrant.core.cache_manager import CacheManager
from agentgrant.core.context import AppContext, pass_context


@click.command("search")
@click.argument("query")
@pass_context
def search_command(app: AppContext, query: str) -> None:
    """Search documentation."""
    client = DocsClient(
        app.settings.docs_base_url,
        cache=CacheManager(app.settings.cache_dir),
        use_cache=not app.no_cache,
    )
    results = app.run(client.search(query))
    payload = [
        {
            "title": result.page.title,
            "slug": result.page.slug,
            "url": str(result.page.url),
            "score": round(result.score, 3),
            "snippet": result.snippet,
        }
        for result in results
    ]
    if app.printer.json_output:
        app.printer.emit(payload, title=f"Search Results: {query}")
        return
    app.printer.table(
        f"Search Results: {query}",
        ["title", "slug", "score", "snippet"],
        [[row["title"], row["slug"], row["score"], row["snippet"]] for row in payload],
    )
