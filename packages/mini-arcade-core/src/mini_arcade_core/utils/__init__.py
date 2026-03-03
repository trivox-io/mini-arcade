"""
Mini Arcade Core Utilities Package
"""

from __future__ import annotations

from .assets import find_assets_root
from .deprecated_decorator import deprecated
from .logging import logger
from .profiler import FrameTimer

__all__ = ["logger", "deprecated", "FrameTimer", "find_assets_root"]
