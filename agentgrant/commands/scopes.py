from __future__ import annotations

from agentgrant.utils.http_client import AgentGrantClient
from agentgrant.utils.printer import Printer


async def render_scopes(client: AgentGrantClient, printer: Printer) -> None:
    payload = await client.get("/scopes")
    if printer.json_output:
        printer.print_json(payload)
        return

    items = payload if isinstance(payload, list) else payload.get("items", [])
    printer.print_table(
        "Scopes",
        ["name", "description"],
        [[item.get("name", ""), item.get("description", "")] for item in items],
    )

