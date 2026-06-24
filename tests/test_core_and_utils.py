from __future__ import annotations

import logging
from pathlib import Path

import pytest
from conftest import RecordingPrinter
from pydantic import BaseModel

from agentgrant.core.cache_manager import CacheManager
from agentgrant.core.context import AppContext
from agentgrant.core.logger import configure_logging
from agentgrant.core.settings import AppSettings, load_settings
from agentgrant.utils.formatter import to_serializable_list
from agentgrant.utils.printer import Printer
from agentgrant.utils.validators import validate_output_format


class SampleModel(BaseModel):
    value: int


class SampleObject:
    def __init__(self) -> None:
        self.value = 3


def test_settings_save_load_reset_and_mask(tmp_path: Path) -> None:
    settings = AppSettings(
        config_path=tmp_path / "config.json",
        cache_dir=tmp_path / "cache",
        log_dir=tmp_path / "logs",
        api_key="abcdef123456",
    )
    assert settings.masked_api_key == "abcd...3456"
    settings.save({"docs_base_url": "https://docs.example.com"})
    loaded = load_settings(config_path=settings.config_path)
    assert loaded.docs_base_url == "https://docs.example.com"
    assert loaded.log_file_path.name == "agentgrant.log"
    settings.reset()
    assert settings.api_key is None


def test_cache_manager_ttl_clear_and_info(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cache = CacheManager(tmp_path)
    cache.write("docs", "llms", {"ok": True})
    monkeypatch.setattr("agentgrant.core.cache_manager.time.time", lambda: 9999999999.0)
    assert cache.read("docs", "missing") is None
    assert cache.read("docs", "llms", ttl_seconds=0) is None
    cache.write("docs", "llms2", {"ok": True})
    info = cache.info()
    assert info["entries"] >= 1
    assert cache.clear() >= 1


def test_configure_logging_creates_parent_directory(tmp_path: Path) -> None:
    log_path = tmp_path / "logs" / "app.log"
    configure_logging(verbose=2, debug=False, log_file=log_path)
    logging.getLogger("test").info("hello")
    assert log_path.parent.exists()


def test_app_context_run(settings: AppSettings) -> None:
    ctx = AppContext(
        settings=settings, printer=RecordingPrinter(), verbose=0, debug=False, no_cache=False
    )

    async def coro() -> int:
        return 5

    assert ctx.run(coro()) == 5


def test_formatter_and_validators() -> None:
    payload = to_serializable_list([SampleModel(value=1), {"value": 2}, SampleObject()])
    assert payload == [{"value": 1}, {"value": 2}, {"value": 3}]
    assert validate_output_format("json") == "json"
    with pytest.raises(Exception):
        validate_output_format("bad")


def test_printer_methods(monkeypatch: pytest.MonkeyPatch) -> None:
    printer = Printer()
    calls: list[object] = []
    monkeypatch.setattr(
        printer.console, "print", lambda *args, **kwargs: calls.append((args, kwargs))
    )
    monkeypatch.setattr(
        printer, "table", lambda *args, **kwargs: calls.append(("table", args, kwargs))
    )
    printer.emit({"value": 1}, title="Payload")
    printer.emit("plain text")
    printer.render_format([{"name": "scope"}], "yaml")
    printer.render_format([{"name": "scope"}], "csv")
    printer.render_format([{"name": "scope"}], "table")
    printer.render_format({"name": "scope"}, "table")
    printer.markdown("# heading")
    printer.success("ok")
    printer.warning("warn")
    printer.error("bad")
    assert calls


def test_json_printer(monkeypatch: pytest.MonkeyPatch) -> None:
    printer = Printer(json_output=True)
    calls: list[object] = []
    monkeypatch.setattr(
        printer.console, "print", lambda *args, **kwargs: calls.append((args, kwargs))
    )
    printer.emit({"value": 1})
    printer.table("title", ["a"], [[1]])
    assert len(calls) == 2
