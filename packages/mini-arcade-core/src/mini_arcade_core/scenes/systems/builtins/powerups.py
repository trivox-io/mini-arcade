"""
Reusable pickup / power-up collection helpers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, Iterable, TypeVar

from mini_arcade_core.engine.entities import BaseEntity
from mini_arcade_core.scenes.systems.phases import SystemPhase
from mini_arcade_core.spaces.collision.intersections import intersects_entities

# pylint: disable=invalid-name
TCtx = TypeVar("TCtx")
# pylint: enable=invalid-name


def _default_enabled_when(_ctx: object) -> bool:
    return True


def _default_predicate(_ctx: object, _entity: BaseEntity) -> bool:
    return True


@dataclass(frozen=True)
class PickupCollisionBinding(Generic[TCtx]):
    """
    Declarative collector-vs-pickup intersection rule.
    """

    collectors_getter: Callable[[TCtx], Iterable[BaseEntity]]
    pickups_getter: Callable[[TCtx], Iterable[BaseEntity]]
    predicate: Callable[[TCtx, BaseEntity], bool] = _default_predicate
    on_collect: Callable[[TCtx, BaseEntity, BaseEntity], None] | None = None
    remove_collected: bool = True


@dataclass
class PickupCollisionSystem(Generic[TCtx]):
    """
    Collect overlapping pickup-like entities and optionally remove them.
    """

    name: str = "common_pickup_collision"
    phase: int = SystemPhase.SIMULATION
    order: int = 48
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    bindings: tuple[PickupCollisionBinding[TCtx], ...] = ()

    def step(self, ctx: TCtx) -> None:
        """Resolve pickup collection for all configured bindings."""

        if not self.enabled_when(ctx):
            return

        ids_to_remove: set[int] = set()
        for binding in self.bindings:
            collectors = tuple(binding.collectors_getter(ctx))
            if not collectors:
                continue

            for pickup in tuple(binding.pickups_getter(ctx)):
                pickup_id = int(pickup.id)
                if pickup_id in ids_to_remove:
                    continue
                if not binding.predicate(ctx, pickup):
                    continue

                for collector in collectors:
                    if not intersects_entities(collector, pickup):
                        continue
                    if binding.on_collect is not None:
                        binding.on_collect(ctx, collector, pickup)
                    if binding.remove_collected:
                        ids_to_remove.add(pickup_id)
                    break

        if ids_to_remove:
            ctx.world.remove_entities_by_ids(ids_to_remove)


__all__ = [
    "PickupCollisionBinding",
    "PickupCollisionSystem",
]
