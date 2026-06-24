from click.testing import CliRunner

from agentgrant.cli import cli
from agentgrant.utils import config as config_module


def test_init_creates_config(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(config_module, "CONFIG_DIR", tmp_path / ".agentgrant")
    monkeypatch.setattr(config_module, "CONFIG_PATH", tmp_path / ".agentgrant" / "config.json")

    runner = CliRunner()
    result = runner.invoke(cli, ["init", "--api-base-url", "https://api.example.com"])

    assert result.exit_code == 0
    assert "Initialized configuration" in result.output
    assert config_module.CONFIG_PATH.exists()


def test_help_lists_commands() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "docs" in result.output
    assert "grant" in result.output
