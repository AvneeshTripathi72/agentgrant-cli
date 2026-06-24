from __future__ import annotations

from pathlib import Path

import pytest

from agentgrant.core.settings import AppSettings


class RecordingPrinter:
    def __init__(self, json_output: bool = False) -> None:
        self.json_output = json_output
        self.calls: list[tuple[str, object, object | None]] = []

    def emit(self, payload: object, title: str | None = None) -> None:
        self.calls.append(("emit", payload, title))

    def table(self, title: str, columns: object, rows: object) -> None:
        self.calls.append(("table", {"title": title, "columns": columns, "rows": rows}, None))

    def markdown(self, content: str) -> None:
        self.calls.append(("markdown", content, None))

    def success(self, message: str) -> None:
        self.calls.append(("success", message, None))

    def warning(self, message: str) -> None:
        self.calls.append(("warning", message, None))

    def error(self, message: str) -> None:
        self.calls.append(("error", message, None))

    def render_format(self, payload: object, output: str) -> None:
        self.calls.append(("render_format", payload, output))


@pytest.fixture()
def settings(tmp_path: Path) -> AppSettings:
    return AppSettings(
        config_path=tmp_path / "config.json",
        cache_dir=tmp_path / "cache",
        log_dir=tmp_path / "logs",
        api_base_url="https://api.example.com",
        docs_base_url="https://docs.example.com",
        api_key="test-api-key-12345678",
        jwt_secret="x" * 32,
        jwt_algorithm="HS256",
    )
