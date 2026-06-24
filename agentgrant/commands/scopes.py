from __future__ import annotations

import click

from agentgrant.commands._shared import create_api_client
from agentgrant.core.context import AppContext, pass_context
from agentgrant.models.scope import Scope
from agentgrant.utils.formatter import to_serializable_list
from agentgrant.utils.validators import validate_output_format


@click.command("scopes")
@click.option("--output", default="table", show_default=True, help="table, json, yaml, or csv")
@pass_context
def scopes_command(app: AppContext, output: str) -> None:
    """List scopes."""
    validate_output_format(output)
    client = create_api_client(app)
    payload = app.run(client.get("/scopes"))
    raw_items = payload if isinstance(payload, list) else payload.get("items", [])
    scopes = [Scope.model_validate(item) for item in raw_items]
    data = to_serializable_list(scopes)
    if output == "table" and not app.printer.json_output:
        app.printer.table(
            "Scopes",
            ["name", "description"],
            [[item["name"], item.get("description", "")] for item in data],
        )
        return
    app.printer.render_format(data, "json" if app.printer.json_output else output)
