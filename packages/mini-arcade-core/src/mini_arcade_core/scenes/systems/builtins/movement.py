"""
Reusable movement helpers for scene pipelines.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable, Generic, Iterable, Literal, Mapping, TypeVar

from mini_arcade_core.engine.entities import BaseEntity
from mini_arcade_core.scenes.systems.phases import SystemPhase

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
        """Translate intent axes into kinematic velocity for bound entities."""

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
        """Integrate velocity and acceleration for bound entities."""

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
    viewport_getter: Callable[[TCtx], tuple[float, float]] = lambda ctx: tuple(
        getattr(ctx.world, "viewport", (0.0, 0.0))
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
        """Apply clamp, wrap, or cull viewport policies to bound entities."""

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


# ---------------------------------------------------------------------------
# Turn / thrust system  (Asteroids-style angular control)
# ---------------------------------------------------------------------------


def _dir_from_angle(
    angle_deg: float, forward_offset_deg: float = -90.0
) -> tuple[float, float]:
    """Unit vector for *angle_deg* with an optional mesh-forward offset."""
    rad = math.radians(angle_deg + forward_offset_deg)
    return (math.cos(rad), math.sin(rad))


@dataclass(frozen=True)
class TurnThrustBinding(Generic[TCtx]):
    """
    Bind turn/thrust intent values to one entity.

    *turn_getter* should return a signed float (negative=left, positive=right).
    *thrust_getter* should return a float (0 = no thrust, positive = forward).
    """

    entity_getter: Callable[[TCtx], BaseEntity | None]
    turn_getter: Callable[[TCtx], float]
    thrust_getter: Callable[[TCtx], float]
    turn_speed_deg: float = 240.0
    thrust_accel: float = 280.0
    max_speed: float = 330.0
    forward_offset_deg: float = -90.0
    predicate: Callable[[TCtx, BaseEntity], bool] = _default_predicate


@dataclass
class TurnThrustSystem(Generic[TCtx]):
    """
    Rotate an entity with turn input and apply forward thrust along
    its heading.  Typical for Asteroids-style ship controls.

    Phase: CONTROL (20), order 20.
    """

    name: str = "common_turn_thrust"
    phase: int = SystemPhase.CONTROL
    order: int = 20
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    bindings: tuple[TurnThrustBinding[TCtx], ...] = ()

    def step(self, ctx: TCtx) -> None:
        """Apply turn and thrust for bound entities."""

        if not self.enabled_when(ctx):
            return

        dt = float(getattr(ctx, "dt", 0.0))

        for binding in self.bindings:
            entity = binding.entity_getter(ctx)
            if entity is None or entity.kinematic is None:
                continue
            if not binding.predicate(ctx, entity):
                continue

            turn = float(binding.turn_getter(ctx))
            thrust = float(binding.thrust_getter(ctx))

            # Rotation
            if abs(turn) > 0.0001:
                entity.rotation_deg = (
                    float(entity.rotation_deg)
                    + turn * binding.turn_speed_deg * dt
                ) % 360.0

            # Thrust along heading
            if thrust > 0.0:
                dx, dy = _dir_from_angle(
                    float(entity.rotation_deg),
                    binding.forward_offset_deg,
                )
                entity.kinematic.velocity.x += (
                    dx * binding.thrust_accel * thrust * dt
                )
                entity.kinematic.velocity.y += (
                    dy * binding.thrust_accel * thrust * dt
                )

            # Speed cap
            if binding.max_speed > 0.0:
                vx = entity.kinematic.velocity.x
                vy = entity.kinematic.velocity.y
                speed2 = vx * vx + vy * vy
                if speed2 > binding.max_speed * binding.max_speed:
                    speed = math.sqrt(speed2)
                    scale = binding.max_speed / speed
                    entity.kinematic.velocity.x *= scale
                    entity.kinematic.velocity.y *= scale


# ---------------------------------------------------------------------------
# Steering / seek system  (homing missiles and simple CPU agents)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SteerSeekBinding(Generic[TCtx]):
    """
    Bind one pursuer entity to a target position.

    *target_getter* returns the position the entity should steer towards,
    or ``None`` when no target is available (entity keeps current heading).
    """

    entity_getter: Callable[[TCtx], BaseEntity | None]
    target_getter: Callable[[TCtx], tuple[float, float] | None]
    max_steer_deg: float = 180.0
    thrust_accel: float = 200.0
    max_speed: float = 300.0
    forward_offset_deg: float = -90.0
    predicate: Callable[[TCtx, BaseEntity], bool] = _default_predicate


@dataclass(frozen=True)
class SteerSeekGroupBinding(Generic[TCtx]):
    """
    Bind a group of pursuing entities to a shared target callback.
    """

    entities_getter: Callable[[TCtx], Iterable[BaseEntity]]
    target_getter: Callable[[TCtx, BaseEntity], tuple[float, float] | None]
    max_steer_deg: float = 180.0
    thrust_accel: float = 200.0
    max_speed: float = 300.0
    forward_offset_deg: float = -90.0
    predicate: Callable[[TCtx, BaseEntity], bool] = _default_predicate


def _angle_toward(
    src_x: float,
    src_y: float,
    dst_x: float,
    dst_y: float,
    forward_offset_deg: float,
) -> float | None:
    """Desired heading (degrees) from *src* to *dst*, or None if coincident."""
    dx = dst_x - src_x
    dy = dst_y - src_y
    if abs(dx) < 0.0001 and abs(dy) < 0.0001:
        return None
    return (math.degrees(math.atan2(dy, dx)) - forward_offset_deg) % 360.0


def _shortest_angular_delta(current_deg: float, target_deg: float) -> float:
    """Shortest signed rotation from *current_deg* to *target_deg*."""
    diff = (target_deg - current_deg) % 360.0
    if diff > 180.0:
        diff -= 360.0
    return diff


@dataclass
class SteerSeekSystem(Generic[TCtx]):
    """
    Steer entities toward a target position each frame.

    The entity rotates toward the target (capped by *max_steer_deg*/s)
    and accelerates along its heading by *thrust_accel*.

    Phase: CONTROL (20), order 22.
    """

    name: str = "common_steer_seek"
    phase: int = SystemPhase.CONTROL
    order: int = 22
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when

    bindings: tuple[SteerSeekBinding[TCtx], ...] = ()
    group_bindings: tuple[SteerSeekGroupBinding[TCtx], ...] = ()

    def _apply(
        self,
        entity: BaseEntity,
        target: tuple[float, float] | None,
        *,
        max_steer_deg: float,
        thrust_accel: float,
        max_speed: float,
        forward_offset_deg: float,
        dt: float,
    ) -> None:
        if entity.kinematic is None:
            return

        # Steer toward target if present
        if target is not None:
            desired = _angle_toward(
                float(entity.transform.center.x),
                float(entity.transform.center.y),
                target[0],
                target[1],
                forward_offset_deg,
            )
            if desired is not None:
                delta = _shortest_angular_delta(
                    float(entity.rotation_deg), desired
                )
                max_turn = max_steer_deg * dt
                clamped = max(-max_turn, min(max_turn, delta))
                entity.rotation_deg = (
                    float(entity.rotation_deg) + clamped
                ) % 360.0

        # Thrust along current heading
        if thrust_accel > 0.0:
            dx, dy = _dir_from_angle(
                float(entity.rotation_deg), forward_offset_deg
            )
            entity.kinematic.velocity.x += dx * thrust_accel * dt
            entity.kinematic.velocity.y += dy * thrust_accel * dt

        # Speed cap
        if max_speed > 0.0:
            vx = entity.kinematic.velocity.x
            vy = entity.kinematic.velocity.y
            speed2 = vx * vx + vy * vy
            if speed2 > max_speed * max_speed:
                speed = math.sqrt(speed2)
                scale = max_speed / speed
                entity.kinematic.velocity.x *= scale
                entity.kinematic.velocity.y *= scale

    def step(self, ctx: TCtx) -> None:
        """Steer and thrust toward targets for bound entities."""

        if not self.enabled_when(ctx):
            return

        dt = float(getattr(ctx, "dt", 0.0))

        for binding in self.bindings:
            entity = binding.entity_getter(ctx)
            if entity is None:
                continue
            if not binding.predicate(ctx, entity):
                continue
            target = binding.target_getter(ctx)
            self._apply(
                entity,
                target,
                max_steer_deg=binding.max_steer_deg,
                thrust_accel=binding.thrust_accel,
                max_speed=binding.max_speed,
                forward_offset_deg=binding.forward_offset_deg,
                dt=dt,
            )

        for grp in self.group_bindings:
            for entity in grp.entities_getter(ctx):
                if not grp.predicate(ctx, entity):
                    continue
                target = grp.target_getter(ctx, entity)
                self._apply(
                    entity,
                    target,
                    max_steer_deg=grp.max_steer_deg,
                    thrust_accel=grp.thrust_accel,
                    max_speed=grp.max_speed,
                    forward_offset_deg=grp.forward_offset_deg,
                    dt=dt,
                )


# ---------------------------------------------------------------------------
# YAML-backed movement profile loading
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MovementProfile:
    """
    Reusable set of movement parameters loadable from a YAML mapping.

    A profile can feed *TurnThrustBinding* or *SteerSeekBinding* parameters
    so games define tuning in data files instead of Python code.
    """

    turn_speed_deg: float = 240.0
    thrust_accel: float = 280.0
    max_speed: float = 330.0
    drag: float | None = None
    forward_offset_deg: float = -90.0
    max_steer_deg: float = 180.0


def movement_profile_from_dict(
    raw: Mapping[str, Any] | None,
) -> MovementProfile:
    """
    Build a :class:`MovementProfile` from a YAML-friendly dictionary.

    Missing keys fall back to ``MovementProfile`` defaults.
    Unrecognised keys are silently ignored.

    Example YAML::

        movement:
          turn_speed_deg: 200
          thrust_accel: 320
          max_speed: 400
          drag: 0.98
    """
    if not isinstance(raw, Mapping):
        return MovementProfile()

    def _float(key: str, default: float) -> float:
        val = raw.get(key)
        if val is None:
            return default
        return float(val)

    def _opt_float(key: str, default: float | None) -> float | None:
        val = raw.get(key)
        if val is None:
            return default
        return float(val)

    return MovementProfile(
        turn_speed_deg=_float("turn_speed_deg", 240.0),
        thrust_accel=_float("thrust_accel", 280.0),
        max_speed=_float("max_speed", 330.0),
        drag=_opt_float("drag", None),
        forward_offset_deg=_float("forward_offset_deg", -90.0),
        max_steer_deg=_float("max_steer_deg", 180.0),
    )
