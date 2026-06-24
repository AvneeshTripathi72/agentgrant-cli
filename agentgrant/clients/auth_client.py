from __future__ import annotations

from agentgrant.clients.api_client import APIClient


class AuthClient:
    def __init__(self, api_client: APIClient) -> None:
        self.api_client = api_client

    async def whoami(self) -> dict[str, object]:
        return await self.api_client.get("/whoami")
