"""
Asset path helpers shared by games.
"""

from __future__ import annotations

import sys
from pathlib import Path


def find_assets_root(anchor: str) -> Path:
    """
    Find an `assets` directory by walking upward from an anchor file path.

    :param anchor: File path used as the search starting point.
    :type anchor: str
    :raises FileNotFoundError: If assets directory cannot be found.
    """
    # pylint: disable=protected-access
    if hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)
        candidate = base / "assets"
        if candidate.is_dir():
            return candidate
    # pylint: enable=protected-access

    here = Path(anchor).resolve()
    for parent in here.parents:
        candidate = parent / "assets"
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError("Could not locate 'assets' directory.")
