from __future__ import annotations

import logging

import click

from agentgrant.commands.cache import cache_group
from agentgrant.commands.completion import completion_command
from agentgrant.commands.config import config_group
from agentgrant.commands.docs import docs_command
from agentgrant.commands.doctor import doctor_command
from agentgrant.commands.grant import grant_group
from agentgrant.commands.identity import identity_group
from agentgrant.commands.page import page_command
from agentgrant.commands.scopes import scopes_command
from agentgrant.commands.search import search_command
from agentgrant.commands.token import token_group
from agentgrant.commands.version import version_command
from agentgrant.core.context import AppContext
from agentgrant.core.context import pass_context as _pass_context
from agentgrant.core.exceptions import AgentGrantError
from agentgrant.core.logger import configure_logging
from agentgrant.core.settings import load_settings
from agentgrant.utils.printer import Printer


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--json-output", is_flag=True, help="Render output as JSON.")
@click.option("-v", "--verbose", count=True, help="Increase log verbosity.")
@click.option("--debug", is_flag=True, help="Enable debug mode and tracebacks.")
@click.option("--no-cache", is_flag=True, help="Disable on-disk caching for this invocation.")
@click.pass_context
def cli(ctx: click.Context, json_output: bool, verbose: int, debug: bool, no_cache: bool) -> None:
    """AgentGrant CLI."""
    settings = load_settings()
    configure_logging(verbose=verbose, debug=debug, log_file=settings.log_file_path)
    printer = Printer(json_output=json_output)
    ctx.obj = AppContext(
        settings=settings,
        printer=printer,
        verbose=verbose,
        debug=debug,
        no_cache=no_cache,
    )


pass_context = _pass_context


@cli.command("init")
@click.option("--api-base-url", default=None, help="Override API base URL.")
@click.option("--docs-base-url", default=None, help="Override docs base URL.")
@click.option("--jwt-algorithm", default=None, help="Default JWT algorithm.")
@pass_context
def init_command(
    app: AppContext,
    api_base_url: str | None,
    docs_base_url: str | None,
    jwt_algorithm: str | None,
) -> None:
    """Initialize configuration."""
    update: dict[str, str] = {}
    if api_base_url:
        update["api_base_url"] = api_base_url
    if docs_base_url:
        update["docs_base_url"] = docs_base_url
    if jwt_algorithm:
        update["jwt_algorithm"] = jwt_algorithm
    app.settings.save(update)
    app.printer.success(f"Initialized configuration at {app.settings.config_path}")


@cli.command()
@click.option("--api-key", prompt=True, hide_input=True, help="Grantex API key.")
@pass_context
def login(app: AppContext, api_key: str) -> None:
    """Store API key."""
    app.settings.save({"api_key": api_key})
    app.printer.success("API key saved.")


@cli.command()
@pass_context
def logout(app: AppContext) -> None:
    """Remove the stored API key."""
    app.settings.save({"api_key": None})
    app.printer.success("API key removed.")


@cli.command()
@pass_context
def whoami(app: AppContext) -> None:
    """Show current auth state."""
    masked = app.settings.masked_api_key
    payload = {
        "api_base_url": app.settings.api_base_url,
        "docs_base_url": app.settings.docs_base_url,
        "api_key": masked,
        "configured": bool(app.settings.api_key),
    }
    app.printer.emit(payload, title="Authentication")


cli.add_command(docs_command)
cli.add_command(search_command)
cli.add_command(page_command)
cli.add_command(scopes_command)
cli.add_command(token_group)
cli.add_command(identity_group)
cli.add_command(grant_group)
cli.add_command(config_group)
cli.add_command(cache_group)
cli.add_command(doctor_command)
cli.add_command(version_command)
cli.add_command(completion_command)


def main() -> None:
    try:
        cli()
    except AgentGrantError as exc:
        logging.getLogger(__name__).debug("AgentGrant error raised", exc_info=True)
        raise click.ClickException(str(exc)) from exc


if __name__ == "__main__":
    main()
