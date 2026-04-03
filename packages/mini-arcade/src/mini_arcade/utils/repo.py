"""
Helpers for resolving the Mini Arcade workspace root.
"""

from __future__ import annotations

from pathlib import Path


def find_repo_root(start_dir: Path | None = None) -> Path | None:
    """
    Resolve the workspace root by walking parents from ``start_dir`` or cwd.
    """

    start = (start_dir or Path.cwd()).resolve()
    candidates = (start, *start.parents)
    for candidate in candidates:
        packages_dir = candidate / "packages"
        if packages_dir.is_dir() and (candidate / "pyproject.toml").exists():
            return candidate
    return None


__all__ = ["find_repo_root"]
