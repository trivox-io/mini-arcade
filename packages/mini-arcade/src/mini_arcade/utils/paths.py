"""
Path utilities for the mini-arcade project.
"""

from __future__ import annotations


def normalize_path(raw_value: str) -> str:
    """
    Normalize a path string by replacing backslashes with forward slashes and
    stripping leading/trailing slashes.

    :param raw_value: The raw path string to normalize.
    :type raw_value: str
    :return: The normalized path string.
    :rtype: str
    :raises ValueError: If the normalized path string is empty.
    """
    normalized = str(raw_value).replace("\\", "/").strip("/")
    if not normalized:
        raise ValueError("Path must be non-empty")
    return normalized
