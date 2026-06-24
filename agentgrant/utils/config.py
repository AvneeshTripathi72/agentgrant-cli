from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


CONFIG_DIR = Path.home() / ".agentgrant"
CONFIG_PATH = CONFIG_DIR / "config.json"


class PersistedConfig(BaseModel):
    api_base_url: str = "https://api.grantex.ai"
    docs_base_url: str = "https://grantex.ai"
    api_key: str | None = None
    jwt_secret: str | None = None
    jwt_algorithm: str = "HS256"


class RuntimeSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AGENTGRANT_",
        env_file=".env",
        extra="ignore",
    )

    api_base_url: str | None = None
    docs_base_url: str | None = None
    api_key: str | None = None
    jwt_secret: str | None = None
    jwt_algorithm: str | None = None


def ensure_config_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_persisted_config() -> PersistedConfig:
    if not CONFIG_PATH.exists():
        return PersistedConfig()
    return PersistedConfig.model_validate_json(CONFIG_PATH.read_text(encoding="utf-8"))


def save_config(config: PersistedConfig) -> None:
    ensure_config_dir()
    CONFIG_PATH.write_text(
        json.dumps(config.model_dump(mode="json"), indent=2) + "\n",
        encoding="utf-8",
    )


def load_settings() -> PersistedConfig:
    persisted = load_persisted_config()
    runtime = RuntimeSettings()
    merged = persisted.model_copy(
        update={key: value for key, value in runtime.model_dump().items() if value is not None}
    )
    return merged
