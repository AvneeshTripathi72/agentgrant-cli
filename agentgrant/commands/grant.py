from __future__ import annotations

from agentgrant.utils.http_client import AgentGrantClient
from agentgrant.utils.printer import Printer


async def render_grant_list(client: AgentGrantClient, printer: Printer) -> None:
    payload = await client.get("/grants")
    if printer.json_output:
        printer.print_json(payload)
        return

    items = payload if isinstance(payload, list) else payload.get("items", [])
    printer.print_table(
        "Grants",
        ["id", "subject", "scope", "status", "expires_at"],
        [
            [
                item.get("id", ""),
                item.get("subject", ""),
                item.get("scope", ""),
                item.get("status", ""),
                item.get("expires_at", ""),
            ]
            for item in items
        ],
    )


async def revoke_grant(client: AgentGrantClient, printer: Printer, grant_id: str) -> None:
    payload = await client.delete(f"/grants/{grant_id}")
    if printer.json_output:
        printer.print_json(payload)
        return
    printer.print_message(f"Grant '{grant_id}' revoked successfully.")

