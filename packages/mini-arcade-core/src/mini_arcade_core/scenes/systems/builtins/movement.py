"""
Reusable movement helpers for scene pipelines.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, Iterable, Literal, TypeVar

from mini_arcade_core.engine.entities import BaseEntity
from mini_arcade_core.scenes.systems.phases import SystemPhase

# TODO: Add a built-in turn/thrust system for Asteroids-style ship control.
# TODO: Add a steering/seek system for homing missiles and simple CPU agents.
# TODO: Add YAML-backed movement profile loading on top of these primitives.

MoveAxis = Literal["x", "y"]
ViewportPolicy = Literal["clamp", "wrap", "cull"]

# pylint: disable=invalid-name
TCtx = TypeVar("TCtx")
# pylint: enable=invalid-name


def _default_enabled_when(_ctx: object) -> bool:
    return True


def _default_speed(entity: BaseEntity) -> float:
    if entity.kinematic is None:
        return 0.0
    return float(entity.kinematic.max_speed)


def _default_dt(ctx: object, _entity: BaseEntity) -> float:
    return float(getattr(ctx, "dt", 0.0))


def _default_predicate(_ctx: object, _entity: BaseEntity) -> bool:
    return True


def _default_margin(_ctx: object, _entity: BaseEntity) -> float:
    return 0.0


def _entity_position(entity: BaseEntity) -> tuple[float, float]:
    return (
        float(entity.transform.center.x),
        float(entity.transform.center.y),
    )


def _entity_size(entity: BaseEntity) -> tuple[float, float]:
    return (
        float(entity.transform.size.width),
        float(entity.transform.size.height),
    )


@dataclass(frozen=True)
class AxisIntentBinding(Generic[TCtx]):
    """
    Bind one intent value to one entity velocity axis.
    """

    entity_getter: Callable[[TCtx], BaseEntity | None]
    value_getter: Callable[[TCtx], float]
    axis: MoveAxis
    speed_getter: Callable[[BaseEntity], float] = _default_speed
    zero_other_axis: bool = False
    predicate: Callable[[TCtx, BaseEntity], bool] = _default_predicate


@dataclass
class IntentAxisVelocitySystem(Generic[TCtx]):
    """
    Convert intent values into entity velocity on one axis.
    """

    name: str = "common_axis_velocity"
    phase: int = SystemPhase.CONTROL
    order: int = 20
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    bindings: tuple[AxisIntentBinding[TCtx], ...] = ()

    def step(self, ctx: TCtx) -> None:
        if not self.enabled_when(ctx):
            return

        for binding in self.bindings:
            entity = binding.entity_getter(ctx)
            if entity is None or entity.kinematic is None:
                continue
            if not binding.predicate(ctx, entity):
                continue

            value = float(binding.value_getter(ctx))
            velocity = value * float(binding.speed_getter(entity))
            if binding.axis == "x":
                entity.kinematic.velocity.x = velocity
                if binding.zero_other_axis:
                    entity.kinematic.velocity.y = 0.0
            else:
                entity.kinematic.velocity.y = velocity
                if binding.zero_other_axis:
                    entity.kinematic.velocity.x = 0.0


@dataclass(frozen=True)
class MotionBinding(Generic[TCtx]):
    """
    Integrate a group of entities with shared motion options.
    """

    entities_getter: Callable[[TCtx], Iterable[BaseEntity]]
    predicate: Callable[[TCtx, BaseEntity], bool] = _default_predicate
    dt_getter: Callable[[TCtx, BaseEntity], float] = _default_dt
    drag: float | None = None
    drag_getter: Callable[[TCtx, BaseEntity], float | None] | None = None
    spin_attr: str | None = None
    ttl_step: bool = False


@dataclass
class KinematicMotionSystem(Generic[TCtx]):
    """
    Integrate kinematic entities, with optional drag, spin, and TTL ticking.
    """

    name: str = "common_kinematic_motion"
    phase: int = SystemPhase.SIMULATION
    order: int = 30
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    bindings: tuple[MotionBinding[TCtx], ...] = ()

    def step(self, ctx: TCtx) -> None:
        if not self.enabled_when(ctx):
            return

        for binding in self.bindings:
            for entity in binding.entities_getter(ctx):
                if entity.kinematic is None:
                    continue
                if not binding.predicate(ctx, entity):
                    continue

                dt = float(binding.dt_getter(ctx, entity))
                entity.kinematic.step(entity.transform, dt)

                if binding.ttl_step and entity.life is not None:
                    entity.life.step(dt)

                drag = binding.drag
                if binding.drag_getter is not None:
                    drag = binding.drag_getter(ctx, entity)
                if drag is not None:
                    entity.kinematic.velocity.x *= float(drag)
                    entity.kinematic.velocity.y *= float(drag)

                if binding.spin_attr is not None:
                    entity.rotation_deg = (
                        float(getattr(entity, "rotation_deg", 0.0))
                        + float(getattr(entity, binding.spin_attr, 0.0)) * dt
                    ) % 360.0


@dataclass(frozen=True)
class ViewportConstraintBinding(Generic[TCtx]):
    """
    Apply one viewport policy to a group of entities.
    """

    entities_getter: Callable[[TCtx], Iterable[BaseEntity]]
    policy: ViewportPolicy
    predicate: Callable[[TCtx, BaseEntity], bool] = _default_predicate
    axes: tuple[MoveAxis, ...] = ("x", "y")
    margin: float = 0.0
    margin_getter: Callable[[TCtx, BaseEntity], float] = _default_margin
    on_cull: Callable[[TCtx, BaseEntity], None] | None = None


@dataclass
class ViewportConstraintSystem(Generic[TCtx]):
    """
    Clamp, wrap, or cull entities against the current viewport.
    """

    name: str = "common_viewport_constraints"
    phase: int = SystemPhase.SIMULATION
    order: int = 40
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    viewport_getter: Callable[[TCtx], tuple[float, float]] = (
        lambda ctx: tuple(getattr(ctx.world, "viewport", (0.0, 0.0)))
    )
    bindings: tuple[ViewportConstraintBinding[TCtx], ...] = ()

    def _clamp(
        self,
        entity: BaseEntity,
        *,
        viewport: tuple[float, float],
        axes: tuple[MoveAxis, ...],
    ) -> None:
        vw, vh = viewport
        x, y = _entity_position(entity)
        width, height = _entity_size(entity)

        if "x" in axes:
            x = max(0.0, min(float(vw) - width, x))
        if "y" in axes:
            y = max(0.0, min(float(vh) - height, y))
        entity.transform.center.x = x
        entity.transform.center.y = y

    def _wrap(
        self,
        entity: BaseEntity,
        *,
        viewport: tuple[float, float],
        axes: tuple[MoveAxis, ...],
        margin: float,
    ) -> None:
        vw, vh = viewport
        x, y = _entity_position(entity)

        if "x" in axes:
            if x < -margin:
                x = float(vw) + margin
            elif x >= float(vw) + margin:
                x = -margin
        if "y" in axes:
            if y < -margin:
                y = float(vh) + margin
            elif y >= float(vh) + margin:
                y = -margin

        entity.transform.center.x = x
        entity.transform.center.y = y

    def _is_outside(
        self,
        entity: BaseEntity,
        *,
        viewport: tuple[float, float],
        margin: float,
    ) -> bool:
        vw, vh = viewport
        x, y = _entity_position(entity)
        width, height = _entity_size(entity)
        return (
            y > (float(vh) + margin)
            or (y + height) < -margin
            or x > (float(vw) + margin)
            or (x + width) < -margin
        )

    def step(self, ctx: TCtx) -> None:
        if not self.enabled_when(ctx):
            return

        viewport = self.viewport_getter(ctx)
        for binding in self.bindings:
            for entity in binding.entities_getter(ctx):
                if not binding.predicate(ctx, entity):
                    continue

                margin = float(binding.margin) + float(
                    binding.margin_getter(ctx, entity)
                )
                if binding.policy == "clamp":
                    self._clamp(entity, viewport=viewport, axes=binding.axes)
                    continue
                if binding.policy == "wrap":
                    self._wrap(
                        entity,
                        viewport=viewport,
                        axes=binding.axes,
                        margin=margin,
                    )
                    continue
                if binding.policy == "cull" and self._is_outside(
                    entity,
                    viewport=viewport,
                    margin=margin,
                ):
                    if binding.on_cull is not None:
                        binding.on_cull(ctx, entity)
