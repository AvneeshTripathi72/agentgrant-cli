from __future__ import annotations

import click

from agentgrant.commands._shared import create_docs_client
from agentgrant.core.context import AppContext, pass_context
from agentgrant.utils.formatter import to_serializable_list


@click.command("docs")
@pass_context
def docs_command(app: AppContext) -> None:
    """Fetch llms.txt and display documentation pages."""
    client = create_docs_client(app)
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
