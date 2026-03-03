"""
Scene Models
"""

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade_core.scenes.sim_scene import (  # type: ignore[import-not-found]
    BaseIntent,
    BaseTickContext,
    BaseWorld,
)


@dataclass
class MinWorld(BaseWorld):
    """Minimal world state for our example scene."""


@dataclass(frozen=True)
class MinIntent(BaseIntent):
    """Minimal intent for our example scene."""


@dataclass
class MinTickContext(BaseTickContext[MinWorld, MinIntent]):
    """Context for a Min scene tick."""
