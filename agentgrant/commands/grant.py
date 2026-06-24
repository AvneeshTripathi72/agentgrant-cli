from __future__ import annotations

import click

from agentgrant.commands._shared import create_api_client
from agentgrant.core.context import AppContext, pass_context
from agentgrant.models.grant import Grant, GrantListResponse
from agentgrant.utils.formatter import to_serializable_list


@click.group("grant")
def grant_group() -> None:
    """Grant operations."""


@grant_group.command("list")
@click.option("--page", "page_number", default=1, show_default=True, type=int)
@click.option("--limit", default=20, show_default=True, type=int)
@click.option("--status", default=None)
@click.option("--user", default=None)
@pass_context
def grant_list(
    app: AppContext,
    page_number: int,
    limit: int,
    status: str | None,
    user: str | None,
) -> None:
    """List grants with filtering."""
    client = create_api_client(app)
    params: dict[str, object] = {"page": page_number, "limit": limit}
    if status:
        params["status"] = status
    if user:
        params["user"] = user
    payload = app.run(client.get("/grants", params=params))
    if isinstance(payload, list):
        response = GrantListResponse(
            items=[Grant.model_validate(item) for item in payload],
            page=page_number,
            limit=limit,
            total=len(payload),
        )
    else:
        items = [Grant.model_validate(item) for item in payload.get("items", [])]
        response = GrantListResponse(
            items=items,
            page=payload.get("page", page_number),
            limit=payload.get("limit", limit),
            total=payload.get("total", len(items)),
        )
    rows = to_serializable_list(response.items)
    if app.printer.json_output:
        app.printer.emit(response.model_dump(mode="json"), title="Grants")
        return
    app.printer.table(
        "Grants",
        ["id", "subject", "scope", "status", "expires_at"],
        [
            [
                r["id"],
                r.get("subject", ""),
                r.get("scope", ""),
                r.get("status", ""),
                r.get("expires_at", ""),
            ]
            for r in rows
        ],
    )


@grant_group.command("revoke")
@click.argument("grant_id")
@pass_context
def grant_revoke(app: AppContext, grant_id: str) -> None:
    """Revoke a grant."""
    client = create_api_client(app)
    payload = app.run(client.delete(f"/grants/{grant_id}"))
    app.printer.emit(payload, title=f"Grant {grant_id} revoked")
