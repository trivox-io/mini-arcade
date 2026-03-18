"""
Animation system helpers for scene pipelines.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Protocol

from mini_arcade_core.engine.components import Anim2D
from mini_arcade_core.scenes.systems.phases import SystemPhase


class HasAnim(Protocol):
    """
    Structural contract for entities with an animation component.
    """

    anim: object | None
    life: object | None


def _is_alive(entity: object) -> bool:
    life = getattr(entity, "life", None)
    if life is not None:
        return bool(getattr(life, "alive", True))
    return bool(getattr(entity, "alive", True))


@dataclass
class AnimationTickSystem:
    """
    Step entity animations during presentation.

    Current entities use ``Anim2D.step(dt)``. A small compatibility path is
    kept for older animation objects that still expose ``update/current_frame``.
    """

    name: str = "common_anim_tick"
    phase: int = SystemPhase.PRESENTATION
    order: int = 0
    get_entities: Callable[[object], Iterable[HasAnim]] = lambda _w: ()

    def step(self, ctx: object) -> None:
        """
        Advance animations for all alive entities provided by ``get_entities``.
        """
        for entity in self.get_entities(ctx.world):
            if not _is_alive(entity):
                continue

            anim = getattr(entity, "anim", None)
            if anim is None:
                continue

            if isinstance(anim, Anim2D):
                anim.step(ctx.dt)
                continue

            if hasattr(anim, "step"):
                anim.step(ctx.dt)
                continue

            if hasattr(anim, "update"):
                anim.update(ctx.dt)
                if hasattr(entity, "texture") and hasattr(
                    anim, "current_frame"
                ):
                    entity.texture = anim.current_frame
