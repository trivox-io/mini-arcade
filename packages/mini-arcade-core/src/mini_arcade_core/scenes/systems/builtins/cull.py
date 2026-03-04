"""
Cull system to remove entities outside the viewport.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

from mini_arcade_core.scenes.systems.phases import SystemPhase
from mini_arcade_core.spaces.physics.kinematics2d import Kinematic2D


class HasBodyAlive(Protocol):
    """Protocol for entities that have a body and an alive status."""

    body: Kinematic2D
    alive: bool


@dataclass
class CullOutOfViewportSystem:
    """
    Rebuilds a list in-place, keeping only alive entities inside viewport.
    Needs:
      - viewport_getter(world) -> (vw, vh)
      - list_getter(world) -> list
      - list_setter(world, new_list)
    """

    name: str = "common_cull_viewport"
    phase: int = SystemPhase.SIMULATION
    order: int = 0

    viewport_getter: Callable[[object], tuple[float, float]] = lambda _w: (
        0,
        0,
    )
    list_getter: Callable[[object], list[HasBodyAlive]] = lambda _w: []
    list_setter: Callable[[object, list[HasBodyAlive]], None] = (
        lambda _w, _lst: None
    )

    def step(self, ctx):
        """Step the system, culling entities outside the viewport."""
        vw, vh = self.viewport_getter(ctx.world)
        items = self.list_getter(ctx.world)

        kept: list[HasBodyAlive] = []
        for e in items:
            if not e.alive:
                continue
            x, y = e.body.position.x, e.body.position.y
            w, h = e.body.size.width, e.body.size.height

            if (y + h) < 0 or y > vh or (x + w) < 0 or x > vw:
                continue
            kept.append(e)

        self.list_setter(ctx.world, kept)
        self.list_setter(ctx.world, kept)
