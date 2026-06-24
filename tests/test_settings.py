from pathlib import Path

from agentgrant.core.settings import load_settings


def test_load_settings_uses_defaults_when_file_missing(tmp_path: Path) -> None:
    settings = load_settings(config_path=tmp_path / "config.json")

    assert settings.api_base_url.startswith("https://")
    assert settings.cache_dir.exists()
