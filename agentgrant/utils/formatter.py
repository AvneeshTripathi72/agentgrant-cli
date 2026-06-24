from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def to_serializable_list(items: Iterable[Any]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for item in items:
        if hasattr(item, "model_dump"):
            normalized.append(item.model_dump(mode="json"))
        elif isinstance(item, dict):
            normalized.append(item)
        else:
            normalized.append(item.__dict__)
    return normalized
