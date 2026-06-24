from __future__ import annotations

from typing import Any, cast

from agentgrant.clients.api_client import APIClient
from agentgrant.core.exceptions import APIError


class AuthClient:
    def __init__(self, api_client: APIClient) -> None:
        self.api_client = api_client

    async def whoami(self) -> dict[str, Any]:
        payload = await self.api_client.get("/whoami")
        if not isinstance(payload, dict):
            raise APIError("Expected object response from /whoami")
        return cast(dict[str, Any], payload)
