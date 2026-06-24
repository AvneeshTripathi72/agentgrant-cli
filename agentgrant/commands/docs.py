from __future__ import annotations

import click

from agentgrant.clients.docs_client import DocsClient
from agentgrant.core.cache_manager import CacheManager
from agentgrant.core.context import AppContext, pass_context
from agentgrant.utils.formatter import to_serializable_list


@click.command("docs")
@pass_context
def docs_command(app: AppContext) -> None:
    """Fetch llms.txt and display documentation pages."""
    client = DocsClient(
        app.settings.docs_base_url,
        cache=CacheManager(app.settings.cache_dir),
        use_cache=not app.no_cache,
    )
    pages = app.run(client.fetch_pages())
    payload = to_serializable_list(pages)
    if app.printer.json_output:
        app.printer.emit(payload, title="Documentation Pages")
        return
    app.printer.table(
        "Documentation Pages",
        ["title", "slug", "url", "description"],
        [
            [page["title"], page["slug"], page["url"], page.get("description", "")]
            for page in payload
        ],
    )
