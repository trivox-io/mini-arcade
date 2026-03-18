"""
Reusable brick-breaker gameplay helpers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Generic, Iterable, TypeVar

from mini_arcade_core.engine.entities import BaseEntity
from mini_arcade_core.scenes.systems.builtins.grid import (
    GridCoord,
    GridLayout,
)
from mini_arcade_core.scenes.systems.phases import SystemPhase

# pylint: disable=invalid-name
TCtx = TypeVar("TCtx")
# pylint: enable=invalid-name


def _default_enabled_when(_ctx: object) -> bool:
    return True


def _default_predicate(_ctx: object, _entity: BaseEntity) -> bool:
    return True


def _entity_rect(entity: BaseEntity) -> tuple[float, float, float, float]:
    return (
        float(entity.transform.center.x),
        float(entity.transform.center.y),
        float(entity.transform.size.width),
        float(entity.transform.size.height),
    )


def _rect_center(
    rect: tuple[float, float, float, float],
) -> tuple[float, float]:
    x, y, w, h = rect
    return (x + (w * 0.5), y + (h * 0.5))


def _rect_overlap(
    a: tuple[float, float, float, float],
    b: tuple[float, float, float, float],
) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return not (
        (ax + aw) <= bx
        or ax >= (bx + bw)
        or (ay + ah) <= by
        or ay >= (by + bh)
    )


@dataclass(frozen=True)
class BounceHit:
    """
    Resolved bounce collision information.
    """

    axis: str
    normal_x: float
    normal_y: float
    penetration: float


# pylint: disable=too-many-locals
def resolve_rect_bounce(
    mover_rect: tuple[float, float, float, float],
    target_rect: tuple[float, float, float, float],
) -> BounceHit | None:
    """
    Resolve the shallowest-axis bounce between two overlapping rects.
    """

    if not _rect_overlap(mover_rect, target_rect):
        return None

    ax, ay, aw, ah = mover_rect
    bx, by, bw, bh = target_rect
    acx, acy = _rect_center(mover_rect)
    bcx, bcy = _rect_center(target_rect)

    overlap_left = (ax + aw) - bx
    overlap_right = (bx + bw) - ax
    overlap_top = (ay + ah) - by
    overlap_bottom = (by + bh) - ay

    pen_x = min(overlap_left, overlap_right)
    pen_y = min(overlap_top, overlap_bottom)

    if pen_x < pen_y:
        normal_x = -1.0 if acx < bcx else 1.0
        return BounceHit(
            axis="x",
            normal_x=normal_x,
            normal_y=0.0,
            penetration=float(pen_x),
        )

    normal_y = -1.0 if acy < bcy else 1.0
    return BounceHit(
        axis="y",
        normal_x=0.0,
        normal_y=normal_y,
        penetration=float(pen_y),
    )


def apply_bounce_hit(entity: BaseEntity, hit: BounceHit) -> None:
    """
    Reposition and reflect one kinematic entity according to a resolved hit.
    """

    if entity.kinematic is None:
        return

    if hit.axis == "x":
        entity.transform.center.x += hit.normal_x * hit.penetration
        entity.kinematic.velocity.x = -float(entity.kinematic.velocity.x)
        return

    entity.transform.center.y += hit.normal_y * hit.penetration
    entity.kinematic.velocity.y = -float(entity.kinematic.velocity.y)


# pylint: disable=too-many-arguments
def reflect_from_viewport(
    entity: BaseEntity,
    *,
    viewport: tuple[float, float],
    bounce_left: bool = True,
    bounce_right: bool = True,
    bounce_top: bool = True,
    bounce_bottom: bool = False,
) -> tuple[str, ...]:
    """
    Reflect one entity from selected viewport sides.
    """

    if entity.kinematic is None:
        return ()

    vw, vh = viewport
    x, y, w, h = _entity_rect(entity)
    hit_sides: list[str] = []

    if bounce_left and x < 0.0:
        entity.transform.center.x = 0.0
        entity.kinematic.velocity.x = abs(float(entity.kinematic.velocity.x))
        hit_sides.append("left")

    if bounce_right and (x + w) > float(vw):
        entity.transform.center.x = float(vw) - w
        entity.kinematic.velocity.x = -abs(float(entity.kinematic.velocity.x))
        hit_sides.append("right")

    if bounce_top and y < 0.0:
        entity.transform.center.y = 0.0
        entity.kinematic.velocity.y = abs(float(entity.kinematic.velocity.y))
        hit_sides.append("top")

    if bounce_bottom and (y + h) > float(vh):
        entity.transform.center.y = float(vh) - h
        entity.kinematic.velocity.y = -abs(float(entity.kinematic.velocity.y))
        hit_sides.append("bottom")

    return tuple(hit_sides)


@dataclass(frozen=True)
class PaddleBouncePolicy:
    """
    Shape outgoing ball direction based on paddle contact point.
    """

    max_bounce_angle_deg: float = 70.0
    min_speed: float = 180.0
    max_speed: float = 420.0
    speed_gain: float = 1.04
    vertical_bias: float = 1.0
    paddle_velocity_influence: float = 0.25

    # pylint: disable=too-many-locals
    def apply(self, ball: BaseEntity, paddle: BaseEntity) -> None:
        """
        Apply paddle-shaped bounce to a ball-like entity.
        """

        if ball.kinematic is None:
            return

        bx, _, bw, _ = _entity_rect(ball)
        px, _, pw, _ = _entity_rect(paddle)
        ball_center_x = bx + (bw * 0.5)
        paddle_center_x = px + (pw * 0.5)
        paddle_half = max(1.0, pw * 0.5)
        normalized = max(
            -1.0,
            min(1.0, (ball_center_x - paddle_center_x) / paddle_half),
        )

        vx = float(ball.kinematic.velocity.x)
        vy = float(ball.kinematic.velocity.y)
        current_speed = max(self.min_speed, (vx * vx + vy * vy) ** 0.5)
        speed = max(
            self.min_speed,
            min(self.max_speed, current_speed * float(self.speed_gain)),
        )

        paddle_vx = (
            float(paddle.kinematic.velocity.x)
            if paddle.kinematic is not None
            else 0.0
        )
        target_vx = (normalized * speed) + (
            paddle_vx * float(self.paddle_velocity_influence)
        )
        target_vx = max(-self.max_speed, min(self.max_speed, target_vx))

        vertical = max(
            self.min_speed * 0.35,
            speed - abs(target_vx),
        ) * float(self.vertical_bias)
        ball.kinematic.velocity.x = target_vx
        ball.kinematic.velocity.y = -abs(vertical)


@dataclass
class BrickState:
    """
    Mutable brick metadata stored inside a brick field.
    """

    hit_points: int = 1
    payload: Any = None

    @property
    def alive(self) -> bool:
        """Return whether this brick still has hit points remaining."""

        return int(self.hit_points) > 0


@dataclass
class BrickField:
    """
    Dense brick layout with per-cell hit points.
    """

    layout: GridLayout
    bricks: dict[GridCoord, BrickState] = field(default_factory=dict)

    def brick_at(self, coord: GridCoord) -> BrickState | None:
        """
        Return the brick state at one cell, if alive.
        """

        brick = self.bricks.get(coord)
        if brick is None or not brick.alive:
            return None
        return brick

    def occupied_cells(self) -> tuple[GridCoord, ...]:
        """
        Return the currently alive brick cells.
        """

        return tuple(
            coord for coord, brick in self.bricks.items() if brick.alive
        )

    def brick_rect(
        self, coord: GridCoord
    ) -> tuple[float, float, float, float]:
        """
        Return the world-space rect for one brick cell.
        """

        return self.layout.cell_rect(coord)

    def apply_damage(
        self, coord: GridCoord, amount: int = 1
    ) -> BrickState | None:
        """
        Damage one brick cell and delete it when hp reaches zero.
        """

        brick = self.brick_at(coord)
        if brick is None:
            return None
        brick.hit_points = max(0, int(brick.hit_points) - int(amount))
        if not brick.alive:
            del self.bricks[coord]
            return None
        return brick


@dataclass(frozen=True)
class ViewportBounceBinding(Generic[TCtx]):
    """
    Declarative viewport bounce rule for one or more ball-like entities.
    """

    entities_getter: Callable[[TCtx], Iterable[BaseEntity]]
    viewport_getter: Callable[[TCtx], tuple[float, float]] = lambda ctx: tuple(
        getattr(ctx.world, "viewport", (0.0, 0.0))
    )
    predicate: Callable[[TCtx, BaseEntity], bool] = _default_predicate
    bounce_left: bool = True
    bounce_right: bool = True
    bounce_top: bool = True
    bounce_bottom: bool = False
    on_bounce: Callable[[TCtx, BaseEntity, tuple[str, ...]], None] | None = (
        None
    )


@dataclass
class ViewportBounceSystem(Generic[TCtx]):
    """
    Reflect ball-like entities from selected viewport sides.
    """

    name: str = "common_viewport_bounce"
    phase: int = SystemPhase.SIMULATION
    order: int = 40
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    bindings: tuple[ViewportBounceBinding[TCtx], ...] = ()

    def step(self, ctx: TCtx) -> None:
        """Reflect configured entities from the active viewport edges."""

        if not self.enabled_when(ctx):
            return

        for binding in self.bindings:
            viewport = binding.viewport_getter(ctx)
            for entity in binding.entities_getter(ctx):
                if not binding.predicate(ctx, entity):
                    continue
                sides = reflect_from_viewport(
                    entity,
                    viewport=viewport,
                    bounce_left=binding.bounce_left,
                    bounce_right=binding.bounce_right,
                    bounce_top=binding.bounce_top,
                    bounce_bottom=binding.bounce_bottom,
                )
                if sides and binding.on_bounce is not None:
                    binding.on_bounce(ctx, entity, sides)


@dataclass(frozen=True)
class BounceCollisionBinding(Generic[TCtx]):
    """
    Declarative ball-vs-rect bounce rule.
    """

    mover_getter: Callable[[TCtx], BaseEntity | None]
    targets_getter: Callable[[TCtx], Iterable[BaseEntity]]
    predicate: Callable[[TCtx, BaseEntity], bool] = _default_predicate
    stop_after_first_hit: bool = True
    on_bounce: (
        Callable[[TCtx, BaseEntity, BaseEntity, BounceHit], None] | None
    ) = None


@dataclass
class BounceCollisionSystem(Generic[TCtx]):
    """
    Reflect one moving rect from one or more target rects.
    """

    name: str = "common_bounce_collision"
    phase: int = SystemPhase.SIMULATION
    order: int = 45
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    bindings: tuple[BounceCollisionBinding[TCtx], ...] = ()

    def step(self, ctx: TCtx) -> None:
        """Resolve mover collisions against rect targets and bounce them."""

        if not self.enabled_when(ctx):
            return

        for binding in self.bindings:
            mover = binding.mover_getter(ctx)
            if mover is None or mover.kinematic is None:
                continue

            mover_rect = _entity_rect(mover)
            for target in binding.targets_getter(ctx):
                if not binding.predicate(ctx, target):
                    continue

                hit = resolve_rect_bounce(mover_rect, _entity_rect(target))
                if hit is None:
                    continue

                apply_bounce_hit(mover, hit)
                if binding.on_bounce is not None:
                    binding.on_bounce(ctx, mover, target, hit)
                mover_rect = _entity_rect(mover)
                if binding.stop_after_first_hit:
                    break


@dataclass(frozen=True)
class BrickFieldCollisionBinding(Generic[TCtx]):
    """
    Declarative ball-vs-brick-field bounce and damage rule.
    """

    mover_getter: Callable[[TCtx], BaseEntity | None]
    field_getter: Callable[[TCtx], BrickField | None]
    damage: int = 1
    on_hit: (
        Callable[
            [TCtx, BaseEntity, GridCoord, BrickState | None, BounceHit], None
        ]
        | None
    ) = None


@dataclass
class BrickFieldCollisionSystem(Generic[TCtx]):
    """
    Reflect a ball-like entity from the first hit brick and damage the field.
    """

    name: str = "common_brick_field_collision"
    phase: int = SystemPhase.SIMULATION
    order: int = 46
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    bindings: tuple[BrickFieldCollisionBinding[TCtx], ...] = ()

    # pylint: disable=too-many-locals
    def step(self, ctx: TCtx) -> None:
        """Bounce a mover from the first hit brick cell and apply damage."""

        if not self.enabled_when(ctx):
            return

        for binding in self.bindings:
            mover = binding.mover_getter(ctx)
            brick_field = binding.field_getter(ctx)
            if mover is None or mover.kinematic is None or brick_field is None:
                continue

            mover_rect = _entity_rect(mover)
            hit_cell: GridCoord | None = None
            hit_result: BounceHit | None = None

            for cell in brick_field.occupied_cells():
                hit = resolve_rect_bounce(
                    mover_rect,
                    brick_field.brick_rect(cell),
                )
                if hit is None:
                    continue
                apply_bounce_hit(mover, hit)
                hit_cell = cell
                hit_result = hit
                break

            if hit_cell is None or hit_result is None:
                continue

            remaining = brick_field.apply_damage(hit_cell, binding.damage)
            if binding.on_hit is not None:
                binding.on_hit(ctx, mover, hit_cell, remaining, hit_result)


__all__ = [
    "BounceCollisionBinding",
    "BounceCollisionSystem",
    "BounceHit",
    "BrickField",
    "BrickFieldCollisionBinding",
    "BrickFieldCollisionSystem",
    "BrickState",
    "PaddleBouncePolicy",
    "ViewportBounceBinding",
    "ViewportBounceSystem",
    "apply_bounce_hit",
    "reflect_from_viewport",
    "resolve_rect_bounce",
]
