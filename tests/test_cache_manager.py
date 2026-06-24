from agentgrant.core.cache_manager import CacheManager


def test_cache_manager_round_trip(tmp_path) -> None:
    cache = CacheManager(tmp_path)
    cache.write("docs", "llms", {"value": 1})

    assert cache.read("docs", "llms") == {"value": 1}
    assert cache.info()["entries"] == 1
