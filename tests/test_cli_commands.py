from __future__ import annotations

import json
import runpy

import jwt
import pytest
from click.testing import CliRunner

from agentgrant.cli import cli, main
from agentgrant.core.exceptions import AgentGrantError
from agentgrant.core.settings import AppSettings
from agentgrant.models.docs import DocsPage, DocsSearchResult


def configure_cli(monkeypatch: pytest.MonkeyPatch, settings: AppSettings) -> None:
    monkeypatch.setattr("agentgrant.cli.load_settings", lambda: settings)
    monkeypatch.setattr("agentgrant.cli.configure_logging", lambda **_: None)


def test_cli_help_shows_groups(monkeypatch: pytest.MonkeyPatch, settings: AppSettings) -> None:
    configure_cli(monkeypatch, settings)
    result = CliRunner().invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "doctor" in result.output
    assert "grant" in result.output


def test_init_login_logout_and_whoami(
    monkeypatch: pytest.MonkeyPatch, settings: AppSettings
) -> None:
    configure_cli(monkeypatch, settings)
    runner = CliRunner()

    result = runner.invoke(cli, ["init", "--api-base-url", "https://override.example.com"])
    assert result.exit_code == 0
    assert "Initialized configuration" in result.output

    result = runner.invoke(cli, ["login", "--api-key", "super-secret-key"])
    assert result.exit_code == 0
    assert "API key saved." in result.output

    result = runner.invoke(cli, ["whoami"])
    assert result.exit_code == 0
    assert "Authentication" in result.output
    assert "supe...-key" in result.output
    assert "configured" in result.output

    result = runner.invoke(cli, ["logout"])
    assert result.exit_code == 0
    assert "API key removed." in result.output


def test_cli_json_output(monkeypatch: pytest.MonkeyPatch, settings: AppSettings) -> None:
    configure_cli(monkeypatch, settings)
    result = CliRunner().invoke(cli, ["--json-output", "whoami"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["api_base_url"] == "https://api.example.com"


def test_completion_and_version(monkeypatch: pytest.MonkeyPatch, settings: AppSettings) -> None:
    configure_cli(monkeypatch, settings)
    runner = CliRunner()
    result = runner.invoke(cli, ["completion", "--shell", "powershell"])
    assert result.exit_code == 0
    assert "powershell_source" in result.output

    result = runner.invoke(cli, ["version"])
    assert result.exit_code == 0
    assert "agentgrant" in result.output


def test_config_group(monkeypatch: pytest.MonkeyPatch, settings: AppSettings) -> None:
    configure_cli(monkeypatch, settings)
    runner = CliRunner()
    result = runner.invoke(cli, ["config", "show"])
    assert result.exit_code == 0
    assert "Configuration" in result.output

    result = runner.invoke(cli, ["config", "set", "api_key", "new-value"])
    assert result.exit_code == 0
    assert "Updated 'api_key'." in result.output

    result = runner.invoke(cli, ["config", "reset"])
    assert result.exit_code == 0
    assert "Configuration reset." in result.output


def test_config_group_rejects_invalid_key(
    monkeypatch: pytest.MonkeyPatch, settings: AppSettings
) -> None:
    configure_cli(monkeypatch, settings)
    result = CliRunner().invoke(cli, ["config", "set", "unsupported", "value"])
    assert result.exit_code != 0
    assert "Unsupported config key" in result.output


def test_docs_search_and_page_commands(
    monkeypatch: pytest.MonkeyPatch, settings: AppSettings
) -> None:
    configure_cli(monkeypatch, settings)
    page = DocsPage(title="Scopes", slug="scopes", url="https://docs.example.com/scopes")
    search_result = DocsSearchResult(page=page, score=4.5, snippet="scope details")

    class FakeDocsClient:
        async def fetch_pages(self) -> list[DocsPage]:
            return [page]

        async def search(self, query: str) -> list[DocsSearchResult]:
            assert query == "scope"
            return [search_result]

        async def resolve_page(self, name: str) -> DocsPage:
            assert name == "scopes"
            return page

        async def fetch_page_content(self, selected: DocsPage) -> str:
            assert selected.slug == "scopes"
            return "Hello docs"

    fake_factory = lambda app: FakeDocsClient()
    monkeypatch.setattr("agentgrant.commands.docs.create_docs_client", fake_factory)
    monkeypatch.setattr("agentgrant.commands.search.create_docs_client", fake_factory)
    monkeypatch.setattr("agentgrant.commands.page.create_docs_client", fake_factory)
    runner = CliRunner()

    assert runner.invoke(cli, ["docs"]).exit_code == 0
    search_result_cli = runner.invoke(cli, ["search", "scope"])
    assert search_result_cli.exit_code == 0
    assert "scope details" in search_result_cli.output

    page_result = runner.invoke(cli, ["page", "scopes"])
    assert page_result.exit_code == 0
    assert "Hello docs" in page_result.output


def test_scopes_identity_grant_cache_and_doctor(
    monkeypatch: pytest.MonkeyPatch, settings: AppSettings
) -> None:
    configure_cli(monkeypatch, settings)

    class FakeApiClient:
        async def get(self, path: str, params: dict[str, object] | None = None) -> object:
            if path == "/scopes":
                return [{"name": "scope:read", "description": "Read scope"}]
            if path == "/identities":
                return [
                    {"id": "user1", "name": "User One", "email": "u@example.com", "type": "human"}
                ]
            if path == "/identities/user1":
                return {
                    "id": "user1",
                    "name": "User One",
                    "email": "u@example.com",
                    "type": "human",
                }
            if path == "/grants":
                return {
                    "items": [
                        {"id": "g1", "subject": "user1", "scope": "scope:read", "status": "active"}
                    ]
                }
            if path == "/health":
                return {"ok": True}
            raise AssertionError((path, params))

        async def delete(self, path: str) -> object:
            assert path == "/grants/g1"
            return {"ok": True}

    fake_factory = lambda app: FakeApiClient()
    monkeypatch.setattr("agentgrant.commands.scopes.create_api_client", fake_factory)
    monkeypatch.setattr("agentgrant.commands.identity.create_api_client", fake_factory)
    monkeypatch.setattr("agentgrant.commands.grant.create_api_client", fake_factory)
    monkeypatch.setattr("agentgrant.commands.doctor.create_api_client", fake_factory)

    runner = CliRunner()
    assert runner.invoke(cli, ["scopes", "--output", "json"]).exit_code == 0
    assert runner.invoke(cli, ["identity", "get", "user1"]).exit_code == 0
    assert runner.invoke(cli, ["identity", "list"]).exit_code == 0
    assert (
        runner.invoke(cli, ["grant", "list", "--status", "active", "--user", "user1"]).exit_code
        == 0
    )
    revoke_result = runner.invoke(cli, ["grant", "revoke", "g1"])
    assert revoke_result.exit_code == 0
    assert "Grant g1 revoked" in revoke_result.output
    assert runner.invoke(cli, ["cache", "info"]).exit_code == 0
    assert runner.invoke(cli, ["cache", "clear"]).exit_code == 0
    assert runner.invoke(cli, ["doctor"]).exit_code == 0


def test_token_commands(monkeypatch: pytest.MonkeyPatch, settings: AppSettings, tmp_path) -> None:
    configure_cli(monkeypatch, settings)
    token = jwt.encode({"sub": "user1"}, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    token_file = tmp_path / "token.jwt"
    token_file.write_text(token, encoding="utf-8")
    runner = CliRunner()

    decode_result = runner.invoke(cli, ["token", "decode", str(token_file)])
    assert decode_result.exit_code == 0
    assert "Decoded JWT" in decode_result.output

    verify_result = runner.invoke(cli, ["token", "verify", str(token_file)])
    assert verify_result.exit_code == 0
    assert "Verified JWT" in verify_result.output


def test_token_verify_requires_secret(
    monkeypatch: pytest.MonkeyPatch, settings: AppSettings
) -> None:
    settings.jwt_secret = None
    configure_cli(monkeypatch, settings)
    token = jwt.encode({"sub": "user1"}, "x" * 32, algorithm="HS256")
    result = CliRunner().invoke(cli, ["token", "verify", token])
    assert result.exit_code != 0
    assert isinstance(result.exception, Exception)
    assert "A JWT secret is required" in str(result.exception)


def test_main_wraps_agentgrant_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "agentgrant.cli.cli", lambda: (_ for _ in ()).throw(AgentGrantError("boom"))
    )
    with pytest.raises(Exception) as exc:
        main()
    assert "boom" in str(exc.value)


def test_module_main_executes(monkeypatch: pytest.MonkeyPatch) -> None:
    called = {"value": False}
    monkeypatch.setattr("agentgrant.cli.main", lambda: called.__setitem__("value", True))
    runpy.run_module("agentgrant.__main__", run_name="__main__")
    assert called["value"] is True
