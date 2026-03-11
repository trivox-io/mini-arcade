"""
Reusable spawn and wave progression systems.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, Iterable, Optional, TypeVar, Union

from mini_arcade_core.engine.entities import BaseEntity
from mini_arcade_core.scenes.systems.phases import SystemPhase

# pylint: disable=invalid-name
TCtx = TypeVar("TCtx")
SpawnResult = Optional[Union[BaseEntity, Iterable[BaseEntity]]]
# pylint: enable=invalid-name


def _default_enabled_when(_ctx: object) -> bool:
    return True


def _normalize_spawned(spawned: SpawnResult) -> tuple[BaseEntity, ...]:
    if spawned is None:
        return ()
    if isinstance(spawned, BaseEntity):
        return (spawned,)
    return tuple(entity for entity in spawned if entity is not None)


@dataclass(frozen=True)
class SpawnBinding(Generic[TCtx]):
    """
    Declarative spawn rule for one spawn source.
    """

    should_spawn: Callable[[TCtx], bool]
    spawn: Callable[[TCtx], SpawnResult]
    on_spawned: Callable[[TCtx, tuple[BaseEntity, ...]], None] | None = None
    insert_into_world: bool = True


@dataclass
class SpawnSystem(Generic[TCtx]):
    """
    Execute reusable spawn rules and insert spawned entities into the world.
    """

    name: str = "common_spawn"
    phase: int = SystemPhase.SIMULATION
    order: int = 25
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    bindings: tuple[SpawnBinding[TCtx], ...] = ()

    def step(self, ctx: TCtx) -> None:
        if not self.enabled_when(ctx):
            return

        for binding in self.bindings:
            if not binding.should_spawn(ctx):
                continue

            spawned = _normalize_spawned(binding.spawn(ctx))
            if not spawned:
                continue

            if binding.insert_into_world:
                ctx.world.entities.extend(spawned)
            if binding.on_spawned is not None:
                binding.on_spawned(ctx, spawned)


@dataclass(frozen=True)
class WaveProgressionBinding(Generic[TCtx]):
    """
    Declarative wave/lap/round progression rule.
    """

    is_complete: Callable[[TCtx], bool]
    can_progress: Callable[[TCtx], bool] = _default_enabled_when
    advance: Callable[[TCtx], None] | None = None
    spawn_next: Callable[[TCtx], SpawnResult] | None = None
    on_spawned: Callable[[TCtx, tuple[BaseEntity, ...]], None] | None = None
    insert_into_world: bool = True


@dataclass
class WaveProgressionSystem(Generic[TCtx]):
    """
    Advance wave state and optionally spawn the next batch when complete.
    """

    name: str = "common_wave_progression"
    phase: int = SystemPhase.SIMULATION
    order: int = 80
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    bindings: tuple[WaveProgressionBinding[TCtx], ...] = ()

    def step(self, ctx: TCtx) -> None:
        if not self.enabled_when(ctx):
            return

        for binding in self.bindings:
            if not binding.can_progress(ctx):
                continue
            if not binding.is_complete(ctx):
                continue

            if binding.advance is not None:
                binding.advance(ctx)

            if binding.spawn_next is None:
                continue

            spawned = _normalize_spawned(binding.spawn_next(ctx))
            if not spawned:
                continue

            if binding.insert_into_world:
                ctx.world.entities.extend(spawned)
            if binding.on_spawned is not None:
                binding.on_spawned(ctx, spawned)


__all__ = [
    "SpawnBinding",
    "SpawnSystem",
    "WaveProgressionBinding",
    "WaveProgressionSystem",
]
