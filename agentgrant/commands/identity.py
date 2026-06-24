from __future__ import annotations

import click

from agentgrant.commands._shared import create_api_client
from agentgrant.core.context import AppContext, pass_context
from agentgrant.models.identity import Identity, IdentityListResponse
from agentgrant.utils.formatter import to_serializable_list


@click.group("identity")
def identity_group() -> None:
    """Identity operations."""


@identity_group.command("get")
@click.argument("identity_id")
@pass_context
def identity_get(app: AppContext, identity_id: str) -> None:
    """Fetch one identity."""
    client = create_api_client(app)
    payload = app.run(client.get(f"/identities/{identity_id}"))
    identity = Identity.model_validate(payload)
    app.printer.emit(identity.model_dump(mode="json"), title=f"Identity {identity_id}")


@identity_group.command("list")
@pass_context
def identity_list(app: AppContext) -> None:
    """List identities."""
    client = create_api_client(app)
    payload = app.run(client.get("/identities"))
    data = payload if isinstance(payload, dict) else {"items": payload}
    identities = IdentityListResponse.model_validate(data)
    rows = to_serializable_list(identities.items)
    if app.printer.json_output:
        app.printer.emit(rows, title="Identities")
        return
    app.printer.table(
        "Identities",
        ["id", "name", "email", "type"],
        [[r["id"], r.get("name", ""), r.get("email", ""), r.get("type", "")] for r in rows],
    )
