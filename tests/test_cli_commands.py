from click.testing import CliRunner

from agentgrant.cli import cli


def test_cli_help_shows_new_commands() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "doctor" in result.output
    assert "completion" in result.output
    assert "config" in result.output


def test_completion_command_runs() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["completion", "--shell", "bash"])

    assert result.exit_code == 0
    assert "_AGENTGRANT_COMPLETE" in result.output
