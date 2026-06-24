from __future__ import annotations

from typing import Any

from agentgrant.core.session import HTTPSession


class APIClient:
    def __init__(self, base_url: str, api_key: str | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    @property
    def headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        async with HTTPSession(headers=self.headers) as session:
            response = await session.request(
                "GET", f"{self.base_url}/{path.lstrip('/')}", params=params
            )
            return response.json()

    async def delete(self, path: str) -> Any:
        async with HTTPSession(headers=self.headers) as session:
            response = await session.request("DELETE", f"{self.base_url}/{path.lstrip('/')}")
            return response.json() if response.content else {"ok": True}
