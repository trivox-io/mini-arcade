"""
Scene Models
"""

from __future__ import annotations

from dataclasses import dataclass, field

from mini_arcade_core.scenes.sim_scene import (  # type: ignore[import-not-found]
    BaseIntent,
    BaseTickContext,
    BaseWorld,
)


@dataclass
class DebugOverlayState:
    """
    Debug Overlay
    """

    enabled: bool = True
    fps_smoothed: float = 0.0
    frame_ms_smoothed: float = 0.0


@dataclass
class MinWorld(BaseWorld):
    """Minimal world state for our example scene."""

    overlay: DebugOverlayState = field(default_factory=DebugOverlayState)


@dataclass(frozen=True)
class MinIntent(BaseIntent):
    """Minimal intent for our example scene."""

    toggle_overlay: bool = False


@dataclass
class MinTickContext(BaseTickContext[MinWorld, MinIntent]):
    """Context for a Min scene tick."""
