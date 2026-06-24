from __future__ import annotations

import click

from agentgrant.core.cache_manager import CacheManager
from agentgrant.core.context import AppContext, pass_context


@click.group("cache")
def cache_group() -> None:
    """Cache operations."""


@cache_group.command("info")
@pass_context
def cache_info(app: AppContext) -> None:
    """Show cache usage."""
    manager = CacheManager(app.settings.cache_dir)
    app.printer.emit(manager.info(), title="Cache Info")


@cache_group.command("clear")
@pass_context
def cache_clear(app: AppContext) -> None:
    """Clear cached docs data."""
    manager = CacheManager(app.settings.cache_dir)
    deleted = manager.clear()
    app.printer.success(f"Cleared {deleted} cache entr{'y' if deleted == 1 else 'ies'}.")
