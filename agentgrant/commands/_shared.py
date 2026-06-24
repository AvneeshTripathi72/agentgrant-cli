from __future__ import annotations

from agentgrant.clients.api_client import APIClient
from agentgrant.clients.docs_client import DocsClient
from agentgrant.core.cache_manager import CacheManager
from agentgrant.core.context import AppContext


def create_api_client(app: AppContext) -> APIClient:
    return APIClient(app.settings.api_base_url, app.settings.api_key)


def create_docs_client(app: AppContext) -> DocsClient:
    return DocsClient(
        app.settings.docs_base_url,
        cache=CacheManager(app.settings.cache_dir),
        use_cache=not app.no_cache,
    )
