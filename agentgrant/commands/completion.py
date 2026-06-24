from __future__ import annotations

import click

from agentgrant.core.context import AppContext, pass_context


@click.command("completion")
@click.option(
    "--shell",
    type=click.Choice(["bash", "zsh", "fish", "powershell"]),
    default="bash",
    show_default=True,
)
@pass_context
def completion_command(app: AppContext, shell: str) -> None:
    """Show shell completion installation instructions."""
    instructions = {
        "bash": 'eval "$(_AGENTGRANT_COMPLETE=bash_source agentgrant)"',
        "zsh": 'eval "$(_AGENTGRANT_COMPLETE=zsh_source agentgrant)"',
        "fish": "eval (env _AGENTGRANT_COMPLETE=fish_source agentgrant)",
        "powershell": (
            "$env:_AGENTGRANT_COMPLETE='powershell_source'; "
            "agentgrant | Out-String | Invoke-Expression"
        ),
    }
    app.printer.emit({"shell": shell, "command": instructions[shell]}, title="Shell Completion")
