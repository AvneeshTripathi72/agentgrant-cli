from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any


class CacheManager:
    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, namespace: str, key: str) -> Path:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self.cache_dir / namespace / f"{digest}.json"

    def read(self, namespace: str, key: str, ttl_seconds: int | None = None) -> Any | None:
        path = self._path_for(namespace, key)
        if not path.exists():
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        created_at = float(payload["created_at"])
        if ttl_seconds is not None and time.time() - created_at > ttl_seconds:
            return None
        return payload["value"]

    def write(self, namespace: str, key: str, value: Any) -> None:
        path = self._path_for(namespace, key)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"created_at": time.time(), "value": value}
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def clear(self) -> int:
        deleted = 0
        for file_path in self.cache_dir.rglob("*.json"):
            file_path.unlink(missing_ok=True)
            deleted += 1
        return deleted

    def info(self) -> dict[str, Any]:
        files = list(self.cache_dir.rglob("*.json"))
        total_bytes = sum(path.stat().st_size for path in files)
        return {
            "cache_dir": str(self.cache_dir),
            "entries": len(files),
            "size_bytes": total_bytes,
        }
