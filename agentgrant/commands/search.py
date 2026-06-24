from __future__ import annotations

import click

from agentgrant.commands._shared import create_docs_client
from agentgrant.core.context import AppContext, pass_context


@click.command("search")
@click.argument("query")
@pass_context
def search_command(app: AppContext, query: str) -> None:
    """Search documentation."""
    client = create_docs_client(app)
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
