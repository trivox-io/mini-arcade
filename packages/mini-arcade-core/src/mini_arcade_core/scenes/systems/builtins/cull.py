"""
Viewport culling helpers for scene pipelines.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

from mini_arcade_core.scenes.systems.phases import SystemPhase


class Cullable(Protocol):
    """
    Structural contract for entities that can be culled.
    """

    transform: object | None
    life: object | None


def _default_alive_getter(item: object) -> bool:
    life = getattr(item, "life", None)
    if life is not None:
        return bool(getattr(life, "alive", True))
    return bool(getattr(item, "alive", True))


def _default_bounds_getter(
    item: object,
) -> tuple[float, float, float, float] | None:
    transform = getattr(item, "transform", None)
    if transform is not None:
        center = getattr(transform, "center", None)
        size = getattr(transform, "size", None)
        if center is not None and size is not None:
            half_w = float(getattr(size, "width", 0.0)) * 0.5
            half_h = float(getattr(size, "height", 0.0)) * 0.5
            cx = float(getattr(center, "x", 0.0))
            cy = float(getattr(center, "y", 0.0))
            return (cx - half_w, cy - half_h, cx + half_w, cy + half_h)

    body = getattr(item, "body", None)
    if body is not None:
        position = getattr(body, "position", None)
        size = getattr(body, "size", None)
        if position is not None and size is not None:
            left = float(getattr(position, "x", 0.0))
            top = float(getattr(position, "y", 0.0))
            width = float(getattr(size, "width", 0.0))
            height = float(getattr(size, "height", 0.0))
            return (left, top, left + width, top + height)

    return None


@dataclass
class CullOutOfViewportSystem:
    """
    Rebuild a list in place, keeping only alive items that overlap viewport.

    ``viewport_getter`` must return ``(vw, vh)`` and list hooks define which
    collection is filtered. Bounds/alive extraction can be customized, but the
    defaults work with current ``BaseEntity`` instances.
    """

    name: str = "common_cull_viewport"
    phase: int = SystemPhase.SIMULATION
    order: int = 0
    viewport_getter: Callable[[object], tuple[float, float]] = lambda _w: (
        0.0,
        0.0,
    )
    list_getter: Callable[[object], list[Cullable]] = lambda _w: []
    list_setter: Callable[[object, list[Cullable]], None] = (
        lambda _w, _lst: None
    )
    bounds_getter: Callable[
        [Cullable], tuple[float, float, float, float] | None
    ] = _default_bounds_getter
    alive_getter: Callable[[Cullable], bool] = _default_alive_getter

    def step(self, ctx: object) -> None:
        """
        Cull non-overlapping or dead items from the configured list.
        """
        vw, vh = self.viewport_getter(ctx.world)
        kept: list[Cullable] = []

        for item in self.list_getter(ctx.world):
            if not self.alive_getter(item):
                continue

            bounds = self.bounds_getter(item)
            if bounds is None:
                kept.append(item)
                continue

            left, top, right, bottom = bounds
            if right < 0.0 or left > float(vw) or bottom < 0.0 or top > float(vh):
                continue
            kept.append(item)

        self.list_setter(ctx.world, kept)
