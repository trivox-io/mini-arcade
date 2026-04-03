from __future__ import annotations


def normalize_path(raw_value: str) -> str:
    normalized = str(raw_value).replace("\\", "/").strip("/")
    if not normalized:
        raise ValueError("Path must be non-empty")
    return normalized
