from __future__ import annotations

from pathlib import Path

APP_NAME = "agentgrant"
APP_DIR = Path.home() / f".{APP_NAME}"
CONFIG_PATH = APP_DIR / "config.json"
CACHE_DIR = APP_DIR / "cache"
LOG_DIR = APP_DIR / "logs"
DEFAULT_DOCS_CACHE_TTL = 3600
DEFAULT_HTTP_TIMEOUT = 20.0
DEFAULT_API_BASE_URL = "https://api.grantex.ai"
DEFAULT_DOCS_BASE_URL = "https://grantex.ai"
SUPPORTED_OUTPUTS = ("table", "json", "yaml", "csv")
VERSION = "0.2.0"
