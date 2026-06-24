from __future__ import annotations

from typing import Any

import httpx

from .config import PersistedConfig


class AgentGrantError(Exception):
    """Base CLI exception."""


class APIRequestError(AgentGrantError):
    """Raised when the API returns an error."""


class AgentGrantClient:
    def __init__(self, settings: PersistedConfig, timeout: float = 20.0) -> None:
        self.settings = settings
        self.timeout = timeout

    @property
    def headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.settings.api_key:
            headers["Authorization"] = f"Bearer {self.settings.api_key}"
        return headers

    async def _request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> Any:
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers, follow_redirects=True) as client:
            try:
                response = await client.request(method, url, params=params, json=json_body)
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                detail = exc.response.text.strip() or exc.response.reason_phrase
                raise APIRequestError(f"{exc.response.status_code} {detail}") from exc
            except httpx.HTTPError as exc:
                raise APIRequestError(str(exc)) from exc

        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            return response.json()
        return response.text

    async def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        return await self._request("GET", self._join_api_path(path), params=params)

    async def delete(self, path: str) -> Any:
        return await self._request("DELETE", self._join_api_path(path))

    async def fetch_text(self, url: str) -> str:
        result = await self._request("GET", url)
        if isinstance(result, str):
            return result
        raise APIRequestError(f"Expected text response from {url}")

    def _join_api_path(self, path: str) -> str:
        return f"{self.settings.api_base_url.rstrip('/')}/{path.lstrip('/')}"

