from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Callable

import click

from agentgrant.commands.docs import render_docs, render_page, render_search
from agentgrant.commands.grant import render_grant_list, revoke_grant
from agentgrant.commands.identity import render_identity
from agentgrant.commands.scopes import render_scopes
from agentgrant.commands.token import render_decoded_token, render_verified_token
from agentgrant.utils.config import CONFIG_PATH, PersistedConfig, load_settings, save_config
from agentgrant.utils.http_client import APIRequestError, AgentGrantClient
from agentgrant.utils.printer import Printer


@dataclass(slots=True)
class AppContext:
    settings: PersistedConfig
    printer: Printer

    @property
    def client(self) -> AgentGrantClient:
        return AgentGrantClient(self.settings)


pass_context = click.make_pass_decorator(AppContext)


def run_async(coro: object) -> None:
    asyncio.run(coro)


def execute(action: Callable[[], None]) -> None:
    try:
        action()
    except (APIRequestError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc


@click.group()
@click.option("--json-output", is_flag=True, help="Render command output as JSON.")
@click.pass_context
def cli(ctx: click.Context, json_output: bool) -> None:
    """AgentGrant CLI."""
    ctx.obj = AppContext(settings=load_settings(), printer=Printer(json_output=json_output))


@cli.command()
@click.option("--api-base-url", default="https://api.grantex.ai", show_default=True)
@click.option("--docs-base-url", default="https://grantex.ai", show_default=True)
@click.option("--jwt-algorithm", default="HS256", show_default=True)
@pass_context
def init(app: AppContext, api_base_url: str, docs_base_url: str, jwt_algorithm: str) -> None:
    """Initialize configuration."""
    config = app.settings.model_copy(
        update={
            "api_base_url": api_base_url,
            "docs_base_url": docs_base_url,
            "jwt_algorithm": jwt_algorithm,
        }
    )
    save_config(config)
    app.printer.print_message(f"Initialized configuration at {CONFIG_PATH}")


@cli.command()
@click.option("--api-key", prompt=True, hide_input=True, help="Grantex API key.")
@pass_context
def login(app: AppContext, api_key: str) -> None:
    """Store API key."""
    config = app.settings.model_copy(update={"api_key": api_key})
    save_config(config)
    app.printer.print_message("API key saved.")


@cli.command()
@pass_context
def docs(app: AppContext) -> None:
    """Fetch llms.txt and display documentation pages."""
    execute(lambda: run_async(render_docs(app.client, app.printer)))


@cli.command()
@click.argument("query")
@pass_context
def search(app: AppContext, query: str) -> None:
    """Search documentation content."""
    execute(lambda: run_async(render_search(app.client, app.printer, query)))


@cli.command()
@click.argument("page_name")
@pass_context
def page(app: AppContext, page_name: str) -> None:
    """Open a documentation page."""
    execute(lambda: run_async(render_page(app.client, app.printer, page_name)))


@cli.command()
@pass_context
def scopes(app: AppContext) -> None:
    """List available scopes."""
    execute(lambda: run_async(render_scopes(app.client, app.printer)))


@cli.group()
def token() -> None:
    """Inspect JWT tokens."""


@token.command("decode")
@click.argument("token_input")
@pass_context
def token_decode(app: AppContext, token_input: str) -> None:
    """Decode a JWT without verifying its signature."""
    execute(lambda: render_decoded_token(app.printer, token_input))


@token.command("verify")
@click.argument("token_input")
@click.option("--secret", help="JWT signing secret override.")
@pass_context
def token_verify(app: AppContext, token_input: str, secret: str | None) -> None:
    """Verify a JWT signature and registered claims."""
    execute(lambda: render_verified_token(app.printer, token_input, app.settings, secret=secret))


@cli.group()
def identity() -> None:
    """Identity operations."""


@identity.command("get")
@click.argument("identity_id")
@pass_context
def identity_get(app: AppContext, identity_id: str) -> None:
    """Fetch identity details."""
    execute(lambda: run_async(render_identity(app.client, app.printer, identity_id)))


@cli.group()
def grant() -> None:
    """Grant operations."""


@grant.command("list")
@pass_context
def grant_list(app: AppContext) -> None:
    """List grants."""
    execute(lambda: run_async(render_grant_list(app.client, app.printer)))


@grant.command("revoke")
@click.argument("grant_id")
@pass_context
def grant_revoke(app: AppContext, grant_id: str) -> None:
    """Revoke a grant."""
    execute(lambda: run_async(revoke_grant(app.client, app.printer, grant_id)))


if __name__ == "__main__":
    cli()
