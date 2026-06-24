from pathlib import Path

from agentgrant.utils import config as config_module
from agentgrant.utils.config import PersistedConfig, load_persisted_config, save_config


def test_save_and_load_config(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(config_module, "CONFIG_DIR", tmp_path / ".agentgrant")
    monkeypatch.setattr(config_module, "CONFIG_PATH", tmp_path / ".agentgrant" / "config.json")

    config = PersistedConfig(api_key="abc123", docs_base_url="https://docs.example.com")
    save_config(config)
    loaded = load_persisted_config()

    assert loaded.api_key == "abc123"
    assert loaded.docs_base_url == "https://docs.example.com"

