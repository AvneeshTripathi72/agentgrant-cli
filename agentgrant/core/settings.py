from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from agentgrant.core.constants import (
    APP_DIR,
    CACHE_DIR,
    CONFIG_PATH,
    DEFAULT_API_BASE_URL,
    DEFAULT_DOCS_BASE_URL,
    LOG_DIR,
)


class StoredConfig(BaseModel):
    api_base_url: str = DEFAULT_API_BASE_URL
    docs_base_url: str = DEFAULT_DOCS_BASE_URL
    api_key: str | None = None
    jwt_secret: str | None = None
    jwt_algorithm: str = "HS256"


class EnvironmentSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AGENTGRANT_", env_file=".env", extra="ignore")

    api_base_url: str | None = None
    docs_base_url: str | None = None
    api_key: str | None = None
    jwt_secret: str | None = None
    jwt_algorithm: str | None = None


class AppSettings(StoredConfig):
    config_path: Path = CONFIG_PATH
    cache_dir: Path = CACHE_DIR
    log_dir: Path = LOG_DIR

    @property
    def masked_api_key(self) -> str | None:
        if not self.api_key:
            return None
        if len(self.api_key) <= 8:
            return "*" * len(self.api_key)
        return f"{self.api_key[:4]}...{self.api_key[-4:]}"

    @property
    def log_file_path(self) -> Path:
        return self.log_dir / "agentgrant.log"

    def ensure_directories(self) -> None:
        APP_DIR.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def save(self, update: dict[str, Any] | None = None) -> None:
        self.ensure_directories()
        payload = self.model_dump()
        if update:
            payload.update(update)
        cleaned = {
            key: value
            for key, value in payload.items()
            if key not in {"config_path", "cache_dir", "log_dir"}
        }
        self.config_path.write_text(json.dumps(cleaned, indent=2) + "\n", encoding="utf-8")
        refreshed = load_settings(config_path=self.config_path)
        self.api_base_url = refreshed.api_base_url
        self.docs_base_url = refreshed.docs_base_url
        self.api_key = refreshed.api_key
        self.jwt_secret = refreshed.jwt_secret
        self.jwt_algorithm = refreshed.jwt_algorithm

    def reset(self) -> None:
        self.config_path.unlink(missing_ok=True)
        self.api_base_url = DEFAULT_API_BASE_URL
        self.docs_base_url = DEFAULT_DOCS_BASE_URL
        self.api_key = None
        self.jwt_secret = None
        self.jwt_algorithm = "HS256"


def load_settings(config_path: Path = CONFIG_PATH) -> AppSettings:
    stored = StoredConfig()
    if config_path.exists():
        stored = StoredConfig.model_validate_json(config_path.read_text(encoding="utf-8"))
    environment = EnvironmentSettings()
    merged = stored.model_copy(
        update={k: v for k, v in environment.model_dump().items() if v is not None}
    )
    settings = AppSettings(**merged.model_dump(), config_path=config_path)
    settings.ensure_directories()
    return settings
