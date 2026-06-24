from __future__ import annotations

import platform
import sys

import click

from agentgrant.core.constants import VERSION
from agentgrant.core.context import AppContext, pass_context


@click.command("version")
@pass_context
def version_command(app: AppContext) -> None:
    """Show CLI and environment versions."""
    payload = {
        "agentgrant": VERSION,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "implementation": platform.python_implementation(),
        "executable": sys.executable,
    }
    app.printer.emit(payload, title="Version")
