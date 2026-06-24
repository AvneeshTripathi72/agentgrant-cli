from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

import click

from agentgrant.core.settings import AppSettings
from agentgrant.utils.printer import Printer


@dataclass(slots=True)
class AppContext:
    settings: AppSettings
    printer: Printer
    verbose: int
    debug: bool
    no_cache: bool

    def run(self, awaitable: Any) -> Any:
        return asyncio.run(awaitable)


pass_context = click.make_pass_decorator(AppContext)
