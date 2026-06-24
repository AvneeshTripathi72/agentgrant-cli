from __future__ import annotations

from types import SimpleNamespace

import httpx
import pytest

from agentgrant.clients.api_client import APIClient
from agentgrant.clients.auth_client import AuthClient
from agentgrant.clients.docs_client import DocsClient
from agentgrant.core.cache_manager import CacheManager
from agentgrant.core.exceptions import APIError, NetworkError
from agentgrant.core.session import HTTPSession
from agentgrant.models.docs import DocsPage


class FakeResponse:
    def __init__(
        self,
        *,
        payload: object | None = None,
        text: str = "",
        content: bytes = b"{}",
        status_error: Exception | None = None,
    ) -> None:
        self._payload = payload
        self.text = text
        self.content = content
        self._status_error = status_error
        self.status_code = 500
        self.reason_phrase = "boom"

    def raise_for_status(self) -> None:
        if self._status_error is not None:
            raise self._status_error

    def json(self) -> object:
        return self._payload


@pytest.mark.asyncio()
async def test_http_session_success_request() -> None:
    session = HTTPSession()
    session._client = SimpleNamespace(request=lambda *args, **kwargs: None)  # type: ignore[assignment]

    async def fake_request(*_: object, **__: object) -> FakeResponse:
        return FakeResponse(payload={"ok": True})

    session._client.request = fake_request  # type: ignore[attr-defined]
    response = await session.request("GET", "https://example.com")
    assert response.json() == {"ok": True}


@pytest.mark.asyncio()
async def test_http_session_requires_context_manager() -> None:
    session = HTTPSession()
    with pytest.raises(RuntimeError):
        await session.request("GET", "https://example.com")


@pytest.mark.asyncio()
async def test_http_session_translates_http_errors() -> None:
    request = httpx.Request("GET", "https://example.com")
    response = httpx.Response(500, request=request, text="nope")
    status_error = httpx.HTTPStatusError("bad", request=request, response=response)
    session = HTTPSession()
    session._client = SimpleNamespace(request=lambda *args, **kwargs: None)  # type: ignore[assignment]

    async def fake_request(*_: object, **__: object) -> FakeResponse:
        return FakeResponse(status_error=status_error, text="nope")

    session._client.request = fake_request  # type: ignore[attr-defined]
    with pytest.raises(APIError):
        await session.request("GET", "https://example.com")


@pytest.mark.asyncio()
async def test_http_session_translates_network_errors() -> None:
    session = HTTPSession()
    session._client = SimpleNamespace(request=lambda *args, **kwargs: None)  # type: ignore[assignment]

    async def fake_request(*_: object, **__: object) -> FakeResponse:
        raise httpx.ReadTimeout("timeout")

    session._client.request = fake_request  # type: ignore[attr-defined]
    with pytest.raises(NetworkError):
        await session.request("GET", "https://example.com")


@pytest.mark.asyncio()
async def test_api_client_headers_and_requests(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, str, dict[str, object] | None]] = []

    class FakeSession:
        def __init__(self, headers: dict[str, str], timeout: float = 20.0) -> None:
            self.headers = headers

        async def __aenter__(self) -> FakeSession:
            return self

        async def __aexit__(self, *_: object) -> None:
            return None

        async def request(self, method: str, url: str, **kwargs: object) -> FakeResponse:
            calls.append((method, url, kwargs.get("params")))  # type: ignore[arg-type]
            if method == "DELETE":
                return FakeResponse(payload={"deleted": True}, content=b"{}")
            return FakeResponse(payload={"ok": True})

    monkeypatch.setattr("agentgrant.clients.api_client.HTTPSession", FakeSession)
    client = APIClient("https://api.example.com/", "token123")
    assert client.headers["Authorization"] == "Bearer token123"
    assert await client.get("/resource", params={"a": 1}) == {"ok": True}
    assert await client.delete("/resource/1") == {"deleted": True}
    assert calls[0][1] == "https://api.example.com/resource"


@pytest.mark.asyncio()
async def test_auth_client_whoami(monkeypatch: pytest.MonkeyPatch) -> None:
    client = AuthClient(SimpleNamespace(get=lambda path: None))

    async def fake_get(_: str) -> object:
        return {"id": "user1"}

    client.api_client.get = fake_get  # type: ignore[assignment]
    assert await client.whoami() == {"id": "user1"}

    async def bad_get(_: str) -> object:
        return ["not-dict"]

    client.api_client.get = bad_get  # type: ignore[assignment]
    with pytest.raises(APIError):
        await client.whoami()


@pytest.mark.asyncio()
async def test_docs_client_fetch_pages_and_content_uses_cache(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    cache = CacheManager(tmp_path)
    page = DocsPage(title="Scopes", slug="scopes", url="https://docs.example.com/scopes")

    class FakeSession:
        async def __aenter__(self) -> FakeSession:
            return self

        async def __aexit__(self, *_: object) -> None:
            return None

        async def request(self, method: str, url: str, **kwargs: object) -> FakeResponse:
            if url.endswith("/llms.txt"):
                return FakeResponse(text="[Scopes](https://docs.example.com/scopes)")
            return FakeResponse(text="scope details")

    monkeypatch.setattr("agentgrant.clients.docs_client.HTTPSession", lambda: FakeSession())
    client = DocsClient("https://docs.example.com", cache=cache)
    pages = await client.fetch_pages()
    assert pages[0].slug == "scopes"
    assert await client.fetch_page_content(page) == "scope details"
    assert await client.fetch_pages()
    assert await client.fetch_page_content(page) == "scope details"


@pytest.mark.asyncio()
async def test_docs_client_search_and_resolve(monkeypatch: pytest.MonkeyPatch) -> None:
    page1 = DocsPage(title="Scopes", slug="scopes", url="https://docs.example.com/scopes")
    page2 = DocsPage(
        title="Delegation", slug="delegation", url="https://docs.example.com/delegation"
    )
    client = DocsClient("https://docs.example.com")

    async def fake_fetch_pages() -> list[DocsPage]:
        return [page1, page2]

    async def fake_fetch_page_content(page: DocsPage) -> str:
        return (
            "Delegation and scopes are both supported."
            if page.slug == "delegation"
            else "Scopes page"
        )

    monkeypatch.setattr(client, "fetch_pages", fake_fetch_pages)
    monkeypatch.setattr(client, "fetch_page_content", fake_fetch_page_content)
    results = await client.search("delegation")
    assert results[0].page.slug == "delegation"
    assert await client.resolve_page("scope") == page1
