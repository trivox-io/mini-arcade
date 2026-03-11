"""
Reusable projectile lifecycle systems.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Generic, Iterable, TypeVar

from mini_arcade_core.engine.entities import BaseEntity
from mini_arcade_core.scenes.systems import SystemBundle
from mini_arcade_core.scenes.systems.builtins.movement import (
    KinematicMotionSystem,
    MotionBinding,
    ViewportConstraintBinding,
    ViewportConstraintSystem,
)
from mini_arcade_core.scenes.systems.phases import SystemPhase

# pylint: disable=invalid-name
TCtx = TypeVar("TCtx")
# pylint: enable=invalid-name


def _default_enabled_when(_ctx: object) -> bool:
    return True


def _default_predicate(_ctx: object, _entity: BaseEntity) -> bool:
    return True


def _default_dt(ctx: object, _entity: BaseEntity) -> float:
    return float(getattr(ctx, "dt", 0.0))


def _default_margin(_ctx: object, _entity: BaseEntity) -> float:
    return 0.0


def _default_keep_entity(entity: BaseEntity) -> bool:
    life = getattr(entity, "life", None)
    if life is not None:
        return bool(getattr(life, "alive", True))
    return bool(getattr(entity, "alive", True))


def _default_on_cull(_ctx: object, entity: BaseEntity) -> None:
    life = getattr(entity, "life", None)
    if life is not None:
        setattr(life, "alive", False)
        return
    if hasattr(entity, "alive"):
        setattr(entity, "alive", False)


@dataclass(frozen=True)
class ProjectileBoundaryBinding(Generic[TCtx]):
    """
    Culling rule for projectile-like entities.
    """

    entities_getter: Callable[[TCtx], Iterable[BaseEntity]]
    predicate: Callable[[TCtx, BaseEntity], bool] = _default_predicate
    margin: float = 0.0
    margin_getter: Callable[[TCtx, BaseEntity], float] = _default_margin
    on_cull: Callable[[TCtx, BaseEntity], None] = _default_on_cull


@dataclass
class ProjectileBoundarySystem(Generic[TCtx]):
    """
    Cull projectile-like entities against the current viewport.
    """

    name: str = "common_projectile_boundary"
    phase: int = SystemPhase.SIMULATION
    order: int = 36
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    bindings: tuple[ProjectileBoundaryBinding[TCtx], ...] = ()
    _constraints: ViewportConstraintSystem[TCtx] = field(
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        self._constraints = ViewportConstraintSystem(
            name=self.name,
            phase=self.phase,
            order=self.order,
            enabled_when=self.enabled_when,
            bindings=tuple(
                ViewportConstraintBinding(
                    entities_getter=binding.entities_getter,
                    policy="cull",
                    predicate=binding.predicate,
                    margin=binding.margin,
                    margin_getter=binding.margin_getter,
                    on_cull=binding.on_cull,
                )
                for binding in self.bindings
            ),
        )

    def step(self, ctx: TCtx) -> None:
        self._constraints.step(ctx)


@dataclass(frozen=True)
class ProjectileCleanupBinding(Generic[TCtx]):
    """
    Cleanup rule for projectile-like entities.
    """

    entities_getter: Callable[[TCtx], Iterable[BaseEntity]]
    keep_entity: Callable[[BaseEntity], bool] = _default_keep_entity
    tracked_ids_attr: str | None = None
    tracked_domain_name: str | None = None


@dataclass
class ProjectileCleanupSystem(Generic[TCtx]):
    """
    Remove dead projectile-like entities and optionally compact tracked ids.
    """

    name: str = "common_projectile_cleanup"
    phase: int = SystemPhase.SIMULATION
    order: int = 46
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    bindings: tuple[ProjectileCleanupBinding[TCtx], ...] = ()

    def step(self, ctx: TCtx) -> None:
        if not self.enabled_when(ctx):
            return

        ids_to_remove: set[int] = set()
        for binding in self.bindings:
            entities = tuple(binding.entities_getter(ctx))
            ids_to_remove.update(
                int(entity.id)
                for entity in entities
                if not binding.keep_entity(entity)
            )

            if (
                binding.tracked_ids_attr is None
                or binding.tracked_domain_name is None
            ):
                continue

            ctx.world.compact_tracked_entity_ids_for(
                attr_name=binding.tracked_ids_attr,
                domain_name=binding.tracked_domain_name,
                keep_entity=binding.keep_entity,
            )

        if ids_to_remove:
            ctx.world.remove_entities_by_ids(ids_to_remove)


@dataclass(frozen=True)
class ProjectileLifecycleBinding(Generic[TCtx]):
    """
    Full projectile lifecycle configuration for motion, culling, and cleanup.
    """

    entities_getter: Callable[[TCtx], Iterable[BaseEntity]]
    predicate: Callable[[TCtx, BaseEntity], bool] = _default_predicate
    dt_getter: Callable[[TCtx, BaseEntity], float] = _default_dt
    drag: float | None = None
    drag_getter: Callable[[TCtx, BaseEntity], float | None] | None = None
    spin_attr: str | None = None
    ttl_step: bool = False
    margin: float = 0.0
    margin_getter: Callable[[TCtx, BaseEntity], float] = _default_margin
    on_cull: Callable[[TCtx, BaseEntity], None] = _default_on_cull
    keep_entity: Callable[[BaseEntity], bool] = _default_keep_entity
    tracked_ids_attr: str | None = None
    tracked_domain_name: str | None = None


@dataclass
class ProjectileLifecycleBundle(SystemBundle[TCtx]):
    """
    Compose motion, boundary, and cleanup for projectile-like entities.
    """

    bindings: tuple[ProjectileLifecycleBinding[TCtx], ...] = ()
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    motion_name: str = "common_projectile_motion"
    motion_phase: int = SystemPhase.SIMULATION
    motion_order: int = 30
    boundary_name: str = "common_projectile_boundary"
    boundary_phase: int = SystemPhase.SIMULATION
    boundary_order: int = 36
    cleanup_name: str = "common_projectile_cleanup"
    cleanup_phase: int = SystemPhase.SIMULATION
    cleanup_order: int = 46
    include_motion: bool = True
    include_boundary: bool = True
    include_cleanup: bool = True
    _motion: KinematicMotionSystem[TCtx] | None = field(
        init=False,
        default=None,
        repr=False,
    )
    _boundary: ProjectileBoundarySystem[TCtx] | None = field(
        init=False,
        default=None,
        repr=False,
    )
    _cleanup: ProjectileCleanupSystem[TCtx] | None = field(
        init=False,
        default=None,
        repr=False,
    )

    def __post_init__(self) -> None:
        if self.include_motion:
            self._motion = KinematicMotionSystem(
                name=self.motion_name,
                phase=self.motion_phase,
                order=self.motion_order,
                enabled_when=self.enabled_when,
                bindings=tuple(
                    MotionBinding(
                        entities_getter=binding.entities_getter,
                        predicate=binding.predicate,
                        dt_getter=binding.dt_getter,
                        drag=binding.drag,
                        drag_getter=binding.drag_getter,
                        spin_attr=binding.spin_attr,
                        ttl_step=binding.ttl_step,
                    )
                    for binding in self.bindings
                ),
            )

        if self.include_boundary:
            self._boundary = ProjectileBoundarySystem(
                name=self.boundary_name,
                phase=self.boundary_phase,
                order=self.boundary_order,
                enabled_when=self.enabled_when,
                bindings=tuple(
                    ProjectileBoundaryBinding(
                        entities_getter=binding.entities_getter,
                        predicate=binding.predicate,
                        margin=binding.margin,
                        margin_getter=binding.margin_getter,
                        on_cull=binding.on_cull,
                    )
                    for binding in self.bindings
                ),
            )

        if self.include_cleanup:
            self._cleanup = ProjectileCleanupSystem(
                name=self.cleanup_name,
                phase=self.cleanup_phase,
                order=self.cleanup_order,
                enabled_when=self.enabled_when,
                bindings=tuple(
                    ProjectileCleanupBinding(
                        entities_getter=binding.entities_getter,
                        keep_entity=binding.keep_entity,
                        tracked_ids_attr=binding.tracked_ids_attr,
                        tracked_domain_name=binding.tracked_domain_name,
                    )
                    for binding in self.bindings
                ),
            )

    def iter_systems(self) -> Iterable[object]:
        systems: list[object] = []
        if self._motion is not None:
            systems.append(self._motion)
        if self._boundary is not None:
            systems.append(self._boundary)
        if self._cleanup is not None:
            systems.append(self._cleanup)
        return tuple(systems)


__all__ = [
    "ProjectileBoundaryBinding",
    "ProjectileBoundarySystem",
    "ProjectileCleanupBinding",
    "ProjectileCleanupSystem",
    "ProjectileLifecycleBinding",
    "ProjectileLifecycleBundle",
]
