"""
Animation system for the mini arcade engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Protocol

from mini_arcade_core.scenes.systems.phases import SystemPhase


class HasAnimSprite(Protocol):
    """Protocol for entities that have an animation and a texture."""

    anim: object | None  # Animation
    texture: int | None


@dataclass
class AnimationTickSystem:
    """System to update animations and set the current frame as texture."""

    name: str = "common_anim_tick"
    phase: int = SystemPhase.PRESENTATION
    order: int = 0
    get_entities: Callable[[object], Iterable[HasAnimSprite]] = lambda _w: ()

    def step(self, ctx):
        """Step the system, updating animations and setting textures."""
        for e in self.get_entities(ctx.world):
            alive = getattr(e, "alive", True)
            if not alive:
                continue
            anim = getattr(e, "anim", None)
            if not anim:
                continue
            anim.update(ctx.dt)
            e.texture = anim.current_frame
            e.texture = anim.current_frame
