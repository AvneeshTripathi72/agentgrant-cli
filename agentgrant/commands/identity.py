from __future__ import annotations

from agentgrant.utils.http_client import AgentGrantClient
from agentgrant.utils.printer import Printer


async def render_identity(client: AgentGrantClient, printer: Printer, identity_id: str) -> None:
    payload = await client.get(f"/identities/{identity_id}")
    printer.emit(payload, title=f"Identity {identity_id}")

