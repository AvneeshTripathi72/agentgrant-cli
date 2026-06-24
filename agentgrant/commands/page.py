from __future__ import annotations

import click

from agentgrant.clients.docs_client import DocsClient
from agentgrant.core.cache_manager import CacheManager
from agentgrant.core.context import AppContext, pass_context


@click.command("page")
@click.argument("name")
@pass_context
def page_command(app: AppContext, name: str) -> None:
    """Open a documentation page."""
    client = DocsClient(
        app.settings.docs_base_url,
        cache=CacheManager(app.settings.cache_dir),
        use_cache=not app.no_cache,
    )
    page = app.run(client.resolve_page(name))
    content = app.run(client.fetch_page_content(page))
    payload = {"page": page.model_dump(mode="json"), "content": content}
    if app.printer.json_output:
        app.printer.emit(payload, title=page.title)
        return
    app.printer.markdown(f"# {page.title}\n\n{content}")
