from __future__ import annotations

from typing import Any

import httpx

from agentgrant.core.constants import DEFAULT_HTTP_TIMEOUT
from agentgrant.core.exceptions import APIError, NetworkError


class HTTPSession:
    def __init__(
        self, headers: dict[str, str] | None = None, timeout: float = DEFAULT_HTTP_TIMEOUT
    ) -> None:
        self.headers = headers or {}
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> HTTPSession:
        self._client = httpx.AsyncClient(
            headers=self.headers,
            timeout=self.timeout,
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, *_: object) -> None:
        if self._client is not None:
            await self._client.aclose()

    async def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        if self._client is None:
            raise RuntimeError("HTTPSession must be used as an async context manager")
        try:
            response = await self._client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as exc:
            raise APIError(
                f"{exc.response.status_code} {exc.response.text or exc.response.reason_phrase}"
            ) from exc
        except httpx.HTTPError as exc:
            raise NetworkError(str(exc)) from exc
