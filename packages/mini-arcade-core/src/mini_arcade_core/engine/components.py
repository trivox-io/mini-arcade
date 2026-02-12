"""
Components for the mini arcade engine.
"""

from dataclasses import dataclass
from typing import Optional

from mini_arcade_core.engine.animation import Animation


@dataclass
class Renderable:
    """Component for renderable entities."""

    texture: Optional[int] = None
    visible: bool = True


@dataclass
class Animated:
    """Component for entities with animations."""

    anim: Optional["Animation"] = None
    texture: Optional[int] = None


@dataclass
class Alive:
    """Component for entities that are alive."""

    alive: bool = True


@dataclass
class TTL:
    """Component for entities with a time-to-live."""

    ttl: float
    alive: bool = True

    def step(self, dt: float) -> None:
        """Step the TTL, marking the entity as not alive if it expires."""
        self.ttl -= dt
        if self.ttl <= 0:
            self.alive = False
