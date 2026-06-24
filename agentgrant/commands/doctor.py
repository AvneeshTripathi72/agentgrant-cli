from __future__ import annotations

import os
import platform
import sys
from pathlib import Path

import click

from agentgrant.commands._shared import create_api_client
from agentgrant.core.context import AppContext, pass_context
from agentgrant.core.exceptions import AgentGrantError


def checkmark(value: bool) -> str:
    return "PASS" if value else "FAIL"


@click.command("doctor")
@pass_context
def doctor_command(app: AppContext) -> None:
    """Run environment diagnostics."""
    python_ok = sys.version_info >= (3, 12)
    config_ok = Path(app.settings.config_path).exists()
    cache_ok = app.settings.cache_dir.exists()
    env = {
        "AGENTGRANT_API_BASE_URL": os.getenv("AGENTGRANT_API_BASE_URL"),
        "AGENTGRANT_DOCS_BASE_URL": os.getenv("AGENTGRANT_DOCS_BASE_URL"),
        "AGENTGRANT_API_KEY": bool(os.getenv("AGENTGRANT_API_KEY")),
        "AGENTGRANT_JWT_SECRET": bool(os.getenv("AGENTGRANT_JWT_SECRET")),
    }
    api_ok = False
    try:
        client = create_api_client(app)
        app.run(client.get("/health"))
        api_ok = True
    except AgentGrantError:
        api_ok = False

    payload = [
        {
            "check": "python_version",
            "status": checkmark(python_ok),
            "detail": platform.python_version(),
        },
        {
            "check": "config_file",
            "status": checkmark(config_ok),
            "detail": str(app.settings.config_path),
        },
        {
            "check": "cache_directory",
            "status": checkmark(cache_ok),
            "detail": str(app.settings.cache_dir),
        },
        {
            "check": "api_connectivity",
            "status": checkmark(api_ok),
            "detail": app.settings.api_base_url,
        },
        {
            "check": "jwt_secret",
            "status": checkmark(bool(app.settings.jwt_secret or env["AGENTGRANT_JWT_SECRET"])),
            "detail": (
                "configured"
                if (app.settings.jwt_secret or env["AGENTGRANT_JWT_SECRET"])
                else "missing"
            ),
        },
        {"check": "environment", "status": "INFO", "detail": str(env)},
    ]
    if app.printer.json_output:
        app.printer.emit(payload, title="Doctor")
        return
    app.printer.table(
        "Doctor",
        ["check", "status", "detail"],
        [[row["check"], row["status"], row["detail"]] for row in payload],
    )
