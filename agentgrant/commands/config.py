from __future__ import annotations

import click

from agentgrant.core.context import AppContext, pass_context


@click.group("config")
def config_group() -> None:
    """Configuration operations."""


@config_group.command("show")
@pass_context
def config_show(app: AppContext) -> None:
    """Display merged configuration."""
    payload = app.settings.model_dump(mode="json")
    payload["api_key"] = app.settings.masked_api_key
    app.printer.emit(payload, title="Configuration")


@config_group.command("set")
@click.argument("key")
@click.argument("value")
@pass_context
def config_set(app: AppContext, key: str, value: str) -> None:
    """Set one config value."""
    if key not in {"api_base_url", "docs_base_url", "api_key", "jwt_secret", "jwt_algorithm"}:
        raise click.ClickException(f"Unsupported config key '{key}'.")
    app.settings.save({key: value})
    app.printer.success(f"Updated '{key}'.")


@config_group.command("reset")
@pass_context
def config_reset(app: AppContext) -> None:
    """Reset config to defaults."""
    app.settings.reset()
    app.printer.success("Configuration reset.")
