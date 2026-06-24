from __future__ import annotations

import pytest
from conftest import RecordingPrinter

from agentgrant.commands.cache import cache_clear, cache_info
from agentgrant.commands.completion import completion_command
from agentgrant.commands.config import config_reset, config_set, config_show
from agentgrant.commands.docs import docs_command
from agentgrant.commands.doctor import checkmark, doctor_command
from agentgrant.commands.grant import grant_list, grant_revoke
from agentgrant.commands.identity import identity_get, identity_list
from agentgrant.commands.page import page_command
from agentgrant.commands.scopes import scopes_command
from agentgrant.commands.search import search_command
from agentgrant.commands.token import token_decode, token_verify
from agentgrant.commands.version import version_command
from agentgrant.core.context import AppContext
from agentgrant.core.settings import AppSettings
from agentgrant.models.docs import DocsPage, DocsSearchResult


def make_app(settings: AppSettings, *, json_output: bool = False) -> AppContext:
    return AppContext(
        settings=settings,
        printer=RecordingPrinter(json_output=json_output),
        verbose=0,
        debug=False,
        no_cache=False,
    )


def test_command_helpers_via_callbacks(
    monkeypatch: pytest.MonkeyPatch, settings: AppSettings
) -> None:
    app = make_app(settings)
    page = DocsPage(title="Scopes", slug="scopes", url="https://docs.example.com/scopes")

    class FakeDocsClient:
        async def fetch_pages(self) -> list[DocsPage]:
            return [page]

        async def search(self, query: str) -> list[DocsSearchResult]:
            return [DocsSearchResult(page=page, score=1.0, snippet=query)]

        async def resolve_page(self, name: str) -> DocsPage:
            return page

        async def fetch_page_content(self, _: DocsPage) -> str:
            return "content"

    class FakeApiClient:
        async def get(self, path: str, params: dict[str, object] | None = None) -> object:
            if path == "/scopes":
                return [{"name": "scope:read", "description": "Read"}]
            if path == "/identities/abc":
                return {"id": "abc", "name": "A"}
            if path == "/identities":
                return [{"id": "abc", "name": "A"}]
            if path == "/grants":
                return [{"id": "g1", "subject": "abc", "scope": "scope:read", "status": "active"}]
            if path == "/health":
                return {"ok": True}
            raise AssertionError((path, params))

        async def delete(self, path: str) -> object:
            return {"deleted": path}

    monkeypatch.setattr("agentgrant.commands.docs.create_docs_client", lambda app: FakeDocsClient())
    monkeypatch.setattr(
        "agentgrant.commands.search.create_docs_client", lambda app: FakeDocsClient()
    )
    monkeypatch.setattr("agentgrant.commands.page.create_docs_client", lambda app: FakeDocsClient())
    monkeypatch.setattr("agentgrant.commands.scopes.create_api_client", lambda app: FakeApiClient())
    monkeypatch.setattr(
        "agentgrant.commands.identity.create_api_client", lambda app: FakeApiClient()
    )
    monkeypatch.setattr("agentgrant.commands.grant.create_api_client", lambda app: FakeApiClient())
    monkeypatch.setattr("agentgrant.commands.doctor.create_api_client", lambda app: FakeApiClient())

    docs_command.callback.__wrapped__(app)
    search_command.callback.__wrapped__(app, "scope")
    page_command.callback.__wrapped__(app, "scopes")
    scopes_command.callback.__wrapped__(app, "table")
    identity_get.callback.__wrapped__(app, "abc")
    identity_list.callback.__wrapped__(app)
    grant_list.callback.__wrapped__(app, 1, 20, None, None)
    grant_revoke.callback.__wrapped__(app, "g1")
    cache_info.callback.__wrapped__(app)
    cache_clear.callback.__wrapped__(app)
    doctor_command.callback.__wrapped__(app)
    version_command.callback.__wrapped__(app)
    completion_command.callback.__wrapped__(app, "bash")
    assert app.printer.calls


def test_config_callbacks(settings: AppSettings) -> None:
    app = make_app(settings)
    config_show.callback.__wrapped__(app)
    config_set.callback.__wrapped__(app, "api_key", "updated")
    config_reset.callback.__wrapped__(app)
    assert app.printer.calls[-1][0] == "success"


def test_config_set_invalid_key_raises(settings: AppSettings) -> None:
    app = make_app(settings)
    with pytest.raises(Exception):
        config_set.callback.__wrapped__(app, "invalid", "value")


def test_token_callbacks(settings: AppSettings, tmp_path) -> None:
    app = make_app(settings)
    token_path = tmp_path / "token.jwt"
    import jwt

    token_path.write_text(
        jwt.encode({"sub": "abc"}, settings.jwt_secret, algorithm=settings.jwt_algorithm),
        encoding="utf-8",
    )
    token_decode.callback.__wrapped__(app, str(token_path))
    token_verify.callback.__wrapped__(app, str(token_path), None, None, None)
    assert app.printer.calls


def test_doctor_checkmark() -> None:
    assert checkmark(True) == "PASS"
    assert checkmark(False) == "FAIL"
