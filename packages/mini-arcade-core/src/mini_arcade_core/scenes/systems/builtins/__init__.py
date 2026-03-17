"""
Built-in systems for scenes.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Generic, Protocol, TypeVar

from mini_arcade_core.engine.entities import BaseEntity
from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.scenes.systems.base_system import BaseSystem
from mini_arcade_core.scenes.systems.phases import SystemPhase
from mini_arcade_core.spaces.math.vec2 import Vec2

from .actions import (  # noqa: E402  (re-export)
    ActionIntentSystem,
    ActionMap,
    ActionSnapshot,
    AxisActionBinding,
    ConfiguredActionIntentSystem,
    DigitalActionBinding,
    action_map_from_bindings_config,
    action_map_from_controls_config,
)
from .animation import AnimationTickSystem  # noqa: E402  (re-export)
from .bomberman import (  # noqa: E402  (re-export)
    ArenaTile,
    BombField,
    BombFuseBinding,
    BombFuseSystem,
    BombPlacementBinding,
    BombPlacementSystem,
    BombState,
    ChainReactionBinding,
    ChainReactionSystem,
    DestructibleTileBinding,
    DestructibleTileSystem,
    ExplosionCellState,
    ExplosionField,
    ExplosionLifetimeBinding,
    ExplosionLifetimeSystem,
    HazardCollisionBinding,
    HazardCollisionSystem,
    arena_tile_map_from_strings,
    blast_cells,
    is_walkable_arena_tile,
    spawn_explosion_from_bomb,
)
from .brick_breaker import (  # noqa: E402  (re-export)
    BounceCollisionBinding,
    BounceCollisionSystem,
    BounceHit,
    BrickField,
    BrickFieldCollisionBinding,
    BrickFieldCollisionSystem,
    BrickState,
    PaddleBouncePolicy,
    ViewportBounceBinding,
    ViewportBounceSystem,
    apply_bounce_hit,
    reflect_from_viewport,
    resolve_rect_bounce,
)
from .capture_hotkeys import (  # noqa: E402  (re-export)
    CaptureHotkey,
    CaptureHotkeysConfig,
    CaptureHotkeysSystem,
    SceneCaptureConfig,
    action_map_from_scene_capture_config,
)
from .cull import CullOutOfViewportSystem  # noqa: E402  (re-export)
from .falling_blocks import (  # noqa: E402  (re-export)
    BagRandomizer,
    BlockBoard,
    BoardRowClearBinding,
    BoardRowClearSystem,
    FallingBlockPiece,
    FallingBlockPieceSpec,
    block_cells_from_strings,
    piece_fits,
)
from .grid import (  # noqa: E402  (re-export)
    CadenceBinding,
    CadenceState,
    CadenceSystem,
    GridBounds,
    GridCellSpawnBinding,
    GridCellSpawnSystem,
    GridCoord,
    GridLayout,
    choose_first_grid_cell,
    free_grid_cells,
    occupied_grid_cells,
)
from .intent_commands import IntentCommandSystem  # noqa: E402  (re-export)
from .maze import (  # noqa: E402  (re-export)
    CardinalDirection,
    CollectibleCollisionBinding,
    CollectibleCollisionSystem,
    CollectibleField,
    CollectibleKind,
    CollectibleState,
    GridNavigationBinding,
    GridNavigationSystem,
    GridNavigatorState,
    ModeTimerBinding,
    ModeTimerState,
    ModeTimerSystem,
    TileMap,
    TimedMode,
    TunnelWrapBinding,
    TunnelWrapSystem,
    available_directions,
    is_junction,
    step_in_direction,
    tile_map_from_strings,
)
from .movement import (  # noqa: E402  (re-export)
    AxisIntentBinding,
    IntentAxisVelocitySystem,
    KinematicMotionSystem,
    MotionBinding,
    MovementProfile,
    SteerSeekBinding,
    SteerSeekGroupBinding,
    SteerSeekSystem,
    TurnThrustBinding,
    TurnThrustSystem,
    ViewportConstraintBinding,
    ViewportConstraintSystem,
    movement_profile_from_dict,
)
from .particles import (  # noqa: E402  (re-export)
    FIRE_ALPHA_RAMP,
    FIRE_COLOR_RAMP,
    FIRE_PARTICLE_PROFILE,
    MAGIC_ALPHA_RAMP,
    MAGIC_COLOR_RAMP,
    MAGIC_PARTICLE_PROFILE,
    POTION_ALPHA_RAMP,
    POTION_COLOR_RAMP,
    POTION_PARTICLE_PROFILE,
    SMOKE_ALPHA_RAMP,
    SMOKE_COLOR_RAMP,
    SMOKE_PARTICLE_PROFILE,
    ProceduralParticle,
    ProceduralParticleBinding,
    ProceduralParticleBundle,
    ProceduralParticleEmitterState,
    ProceduralParticleProfile,
    ProceduralParticleRenderSystem,
    ProceduralParticleSimulationSystem,
    fire_particle_binding,
    magic_particle_binding,
    particle_binding_with_profile,
    potion_particle_binding,
    smoke_particle_binding,
)
from .pause import IntentPauseSystem  # noqa: E402  (re-export)
from .projectiles import (  # noqa: E402  (re-export)
    ProjectileBoundaryBinding,
    ProjectileBoundarySystem,
    ProjectileCleanupBinding,
    ProjectileCleanupSystem,
    ProjectileLifecycleBinding,
    ProjectileLifecycleBundle,
)
from .spawn import (  # noqa: E402  (re-export)
    SpawnBinding,
    SpawnSystem,
    WaveProgressionBinding,
    WaveProgressionSystem,
)

if TYPE_CHECKING:
    from mini_arcade_core.scenes.sim_scene import BaseIntent
else:
    BaseIntent = object


def _draw_call(drawable: object, ctx: object) -> object:
    """
    Build DrawCall lazily to avoid importing sim_scene at module import time.
    """
    # pylint: disable=import-outside-toplevel
    from mini_arcade_core.scenes.sim_scene import DrawCall

    # pylint: enable=import-outside-toplevel
    return DrawCall(drawable=drawable, ctx=ctx)


def _submit_render_queue(*, layers: tuple[str, ...] | None = None) -> object:
    """
    Build SubmitRenderQueue lazily to avoid import cycles.
    """
    # pylint: disable=import-outside-toplevel
    from mini_arcade_core.scenes.sim_scene import SubmitRenderQueue

    # pylint: enable=import-outside-toplevel
    return SubmitRenderQueue(layers=layers)


def _entity_fill_color(entity: BaseEntity) -> tuple[int, ...] | None:
    style = entity.style
    fill = getattr(style, "fill", None) if style is not None else None
    if fill is None:
        return None
    color = getattr(fill, "color", fill)
    if isinstance(color, (tuple, list)):
        return tuple(color)
    return None


def _entity_stroke(entity: BaseEntity) -> tuple[tuple[int, ...] | None, float]:
    style = entity.style
    stroke = getattr(style, "stroke", None) if style is not None else None
    if stroke is None:
        return (None, 1.0)

    color = getattr(stroke, "color", None)
    if isinstance(color, list):
        color = tuple(color)
    thickness = float(getattr(stroke, "thickness", 1.0))
    return (color if isinstance(color, tuple) else None, thickness)


def _entity_layer(entity: BaseEntity) -> str:
    layer = getattr(entity, "render_layer", "world")
    return str(layer) if layer else "world"


def _rotate_vec(vec: Vec2, angle_deg: float) -> Vec2:
    if abs(angle_deg) <= 0.0001:
        return Vec2(vec.x, vec.y)
    rad = math.radians(angle_deg)
    cs = math.cos(rad)
    sn = math.sin(rad)
    return Vec2((vec.x * cs) - (vec.y * sn), (vec.x * sn) + (vec.y * cs))


def _poly_points(
    *,
    origin: Vec2,
    size: object,
    points: list[Vec2],
    angle_deg: float,
) -> list[Vec2]:
    if not points:
        return []

    is_normalized = all(
        abs(float(p.x)) <= 1.5 and abs(float(p.y)) <= 1.5 for p in points
    )
    scale_x = float(size.width) * 0.5 if is_normalized else 1.0
    scale_y = float(size.height) * 0.5 if is_normalized else 1.0

    out: list[Vec2] = []
    for point in points:
        local = Vec2(float(point.x) * scale_x, float(point.y) * scale_y)
        rotated = _rotate_vec(local, angle_deg)
        out.append(Vec2(origin.x + rotated.x, origin.y + rotated.y))
    return out


class RenderSystemContext(Protocol):
    """
    Structural context contract for render systems.

    Any scene tick context that provides these attributes will be accepted.
    """

    world: object
    draw_ops: list[object] | None
    render_queue: object
    packet: RenderPacket | None


# pylint: disable=invalid-name
# Generic tick-context type used by render systems.
TTickContext = TypeVar("TTickContext", bound=RenderSystemContext)
# pylint: enable=invalid-name


@dataclass
class InputIntentSystem(BaseSystem):
    """
    Converts InputFrame -> MenuIntent.

    :ivar name: Name of the system - default is "base_input".
    :ivar order: Execution order of the system - default is 10.
    """

    name: str = "base_input"
    phase: int = SystemPhase.INPUT
    order: int = 10

    def build_intent(self, ctx: object) -> BaseIntent:
        """Build the intent"""
        raise NotImplementedError

    def step(self, ctx: object):
        """Step the input system to extract menu intent."""
        ctx.intent = self.build_intent(ctx)


@dataclass
class BaseRenderSystem(BaseSystem[TTickContext], Generic[TTickContext]):
    """
    Base rendering system.

    :ivar name: Name of the system - default is "base_render".
    :ivar order: Execution order of the system - default is 100.
    """

    name: str = "base_render"
    phase: int = SystemPhase.RENDERING
    order: int = 100

    def build_draw_ops(self, ctx: TTickContext) -> list[object]:
        """
        Build draw calls for the current tick context.

        :param ctx: The tick context containing world state and other info.
        :type ctx: BaseTickContext
        :return: A list of draw calls to be executed by the render pipeline.
        :rtype: list[DrawCall]
        """
        # Default behavior: subclasses may set ctx.draw_ops directly (Pong style)
        return list(ctx.draw_ops or [])

    def step(self, ctx: TTickContext) -> None:
        ctx.draw_ops = self.build_draw_ops(ctx)
        ctx.packet = RenderPacket.from_ops(ctx.draw_ops)


@dataclass(frozen=True)
class RenderOverlay(Generic[TTickContext]):
    """
    Declarative overlay that emits draw operations into a render queue.
    """

    emit: Callable[[TTickContext, object], None]

    @classmethod
    def from_drawable(
        cls,
        drawable: object,
        *,
        layer: str = "ui",
        z: int = 0,
    ) -> "RenderOverlay[TTickContext]":
        """
        Build an overlay that submits one drawable as a custom queue op.
        """

        def _emit(ctx: TTickContext, rq: object) -> None:
            rq.custom(
                op=_draw_call(drawable, ctx),
                layer=layer,
                z=z,
            )

        return cls(emit=_emit)


@dataclass(frozen=True)
class EntityRenderRule(Generic[TTickContext]):
    """
    First-match-wins entity rendering override rule.
    """

    matches: Callable[[TTickContext, BaseEntity], bool]
    emit: Callable[[TTickContext, object, BaseEntity], None]


@dataclass
class BaseQueuedRenderSystem(
    BaseRenderSystem[TTickContext], Generic[TTickContext]
):
    """
    Base class for render systems that build a RenderQueue and submit it.
    Subclasses can override ``emit`` and/or ``emit_entity`` hooks.
    """

    name: str = "queued_render"
    merge_existing_draw_ops: bool = True

    def emit(self, ctx: TTickContext, rq: object) -> None:
        """
        Emit draw calls into the render queue.

        :param ctx: The tick context containing world state and other info.
        :type ctx: BaseTickContext
        :param rq: The render queue to emit draw calls into.
        :type rq: RenderQueue
        """

        for entity in ctx.world.entities or []:
            self.emit_entity(ctx, rq, entity)

    # pylint: disable=too-many-locals,too-many-return-statements
    def emit_default_entity(
        self, _ctx: TTickContext, rq: object, entity: BaseEntity
    ) -> None:
        """
        Emit the default built-in representation for one entity.
        """
        if not bool(getattr(entity, "render_visible", True)):
            return

        t = entity.transform
        shape = entity.shape
        z = entity.z_index
        layer = _entity_layer(entity)
        fill_color = _entity_fill_color(entity)
        stroke_color, stroke_thickness = _entity_stroke(entity)
        color = fill_color or stroke_color or (255, 255, 255, 255)
        angle_deg = float(getattr(entity, "rotation_deg", 0.0))

        # Component-driven rendering: anim/sprite first, shape fallback.
        if entity.anim is not None and entity.anim.texture is not None:
            rq.texture(
                tex_id=entity.anim.texture,
                x=t.center.x,
                y=t.center.y,
                w=t.size.width,
                h=t.size.height,
                angle_deg=angle_deg,
                layer=layer,
                z=z,
            )
            return

        if entity.sprite is not None:
            rq.texture(
                tex_id=entity.sprite.texture,
                x=t.center.x,
                y=t.center.y,
                w=t.size.width,
                h=t.size.height,
                angle_deg=angle_deg,
                layer=layer,
                z=z,
            )
            return

        if shape.kind == "rect":
            rq.rect(
                center=t.center,
                size=t.size,
                color=color,
                layer=layer,
                z=z,
            )
            return

        if shape.kind == "line":
            a = _rotate_vec(shape.a, angle_deg)
            b = _rotate_vec(shape.b, angle_deg)
            rq.line(
                a=Vec2(t.center.x + a.x, t.center.y + a.y),
                b=Vec2(t.center.x + b.x, t.center.y + b.y),
                color=stroke_color or color,
                thickness=stroke_thickness,
                dash_length=getattr(shape, "dash_length", None),
                dash_gap=getattr(shape, "dash_gap", None),
                layer=layer,
                z=z,
            )
            return

        if shape.kind == "circle":
            r = shape.radius or (min(t.size.width, t.size.height) * 0.5)
            rq.circle(
                center=Vec2(t.center.x + r, t.center.y + r),
                radius=r,
                color=color,
                layer=layer,
                z=z,
            )
            return

        if shape.kind == "triangle":
            points = _poly_points(
                origin=t.center,
                size=t.size,
                points=[
                    Vec2(0.0, -1.0),
                    Vec2(+1.0, +1.0),
                    Vec2(-1.0, +1.0),
                ],
                angle_deg=angle_deg,
            )
            if fill_color is None and stroke_color is not None:
                rq.poly(
                    points=points,
                    fill=None,
                    stroke=stroke_color,
                    thickness=int(round(stroke_thickness)),
                    closed=True,
                    layer=layer,
                    z=z,
                )
            else:
                rq.poly(
                    points=points,
                    fill=color,
                    stroke=None,
                    thickness=0,
                    closed=True,
                    layer=layer,
                    z=z,
                )
            return

        if shape.kind == "poly" and shape.points:
            points = _poly_points(
                origin=t.center,
                size=t.size,
                points=shape.points,
                angle_deg=angle_deg,
            )
            rq.poly(
                points=points,
                fill=fill_color,
                stroke=stroke_color,
                thickness=int(round(stroke_thickness)),
                closed=True,
                layer=layer,
                z=z,
            )

    # pylint: disable=too-many-locals
    def emit_entity(
        self, _ctx: TTickContext, rq: object, entity: BaseEntity
    ) -> None:
        """
        Emit a single entity into the render queue.

        Subclasses can override this hook for entity-specific rendering,
        then delegate back to ``super().emit_entity`` for default behavior.
        """
        self.emit_default_entity(_ctx, rq, entity)

    def build_draw_ops(self, ctx: TTickContext) -> list[object]:
        rq = ctx.render_queue
        rq.clear()
        self.emit(ctx, rq)
        queued_ops = [_draw_call(_submit_render_queue(), ctx)]
        if not self.merge_existing_draw_ops:
            return queued_ops

        extra_ops = list(ctx.draw_ops or [])
        # Render queue first, then additional DrawCall-based overlays.
        return [*queued_ops, *extra_ops]

    @staticmethod
    def _build_pass_ops(ctx: TTickContext) -> dict[str, tuple[object, ...]]:
        layer_map: dict[str, tuple[str, ...]] = {
            "world": ("world", "debug"),
            "lighting": ("lighting",),
            "ui": ("ui",),
            "effects": ("effects", "postfx"),
        }
        out: dict[str, tuple[object, ...]] = {}
        for pass_name, layers in layer_map.items():
            if not ctx.render_queue.iter_sorted(layers):
                continue
            out[pass_name] = (
                _draw_call(_submit_render_queue(layers=layers), ctx),
            )
        return out

    def step(self, ctx: TTickContext) -> None:
        draw_ops = self.build_draw_ops(ctx)
        pass_ops = self._build_pass_ops(ctx)
        if self.merge_existing_draw_ops and ctx.draw_ops:
            pass_ops["world"] = (
                *pass_ops.get("world", tuple()),
                *list(ctx.draw_ops),
            )
        ctx.draw_ops = draw_ops
        ctx.packet = RenderPacket.from_ops(draw_ops, pass_ops=pass_ops)


@dataclass
class ConfiguredQueuedRenderSystem(
    BaseQueuedRenderSystem[TTickContext], Generic[TTickContext]
):
    """
    Queue-based render system composed from overlay and entity override rules.
    """

    overlays: tuple[RenderOverlay[TTickContext], ...] = ()
    entity_rules: tuple[EntityRenderRule[TTickContext], ...] = ()

    def emit(self, ctx: TTickContext, rq: object) -> None:
        super().emit(ctx, rq)
        for overlay in self.overlays:
            overlay.emit(ctx, rq)

    def emit_entity(
        self, ctx: TTickContext, rq: object, entity: BaseEntity
    ) -> None:
        for rule in self.entity_rules:
            if not rule.matches(ctx, entity):
                continue
            rule.emit(ctx, rq, entity)
            return
        super().emit_entity(ctx, rq, entity)


__all__ = [
    "ActionIntentSystem",
    "ActionMap",
    "ActionSnapshot",
    "AnimationTickSystem",
    "AxisActionBinding",
    "BaseQueuedRenderSystem",
    "BaseRenderSystem",
    "BagRandomizer",
    "ArenaTile",
    "BlockBoard",
    "BombField",
    "BombFuseBinding",
    "BombFuseSystem",
    "BombPlacementBinding",
    "BombPlacementSystem",
    "BombState",
    "BounceCollisionBinding",
    "BounceCollisionSystem",
    "BounceHit",
    "BoardRowClearBinding",
    "BoardRowClearSystem",
    "BrickField",
    "BrickFieldCollisionBinding",
    "BrickFieldCollisionSystem",
    "BrickState",
    "FallingBlockPiece",
    "FallingBlockPieceSpec",
    "CaptureHotkey",
    "CaptureHotkeysConfig",
    "CaptureHotkeysSystem",
    "CadenceBinding",
    "CadenceState",
    "CadenceSystem",
    "CardinalDirection",
    "ChainReactionBinding",
    "ChainReactionSystem",
    "CollectibleCollisionBinding",
    "CollectibleCollisionSystem",
    "CollectibleField",
    "CollectibleKind",
    "CollectibleState",
    "ConfiguredActionIntentSystem",
    "ConfiguredQueuedRenderSystem",
    "CullOutOfViewportSystem",
    "DigitalActionBinding",
    "DestructibleTileBinding",
    "DestructibleTileSystem",
    "EntityRenderRule",
    "ExplosionCellState",
    "ExplosionField",
    "ExplosionLifetimeBinding",
    "ExplosionLifetimeSystem",
    "GridBounds",
    "GridNavigationBinding",
    "GridNavigationSystem",
    "GridNavigatorState",
    "GridCellSpawnBinding",
    "GridCellSpawnSystem",
    "GridCoord",
    "GridLayout",
    "HazardCollisionBinding",
    "HazardCollisionSystem",
    "InputIntentSystem",
    "IntentAxisVelocitySystem",
    "IntentCommandSystem",
    "IntentPauseSystem",
    "KinematicMotionSystem",
    "ModeTimerBinding",
    "ModeTimerState",
    "ModeTimerSystem",
    "MotionBinding",
    "FIRE_COLOR_RAMP",
    "FIRE_PARTICLE_PROFILE",
    "FIRE_ALPHA_RAMP",
    "MAGIC_ALPHA_RAMP",
    "MAGIC_COLOR_RAMP",
    "MAGIC_PARTICLE_PROFILE",
    "ProjectileBoundaryBinding",
    "ProjectileBoundarySystem",
    "ProjectileCleanupBinding",
    "ProjectileCleanupSystem",
    "ProjectileLifecycleBinding",
    "ProjectileLifecycleBundle",
    "ProceduralParticle",
    "ProceduralParticleBinding",
    "ProceduralParticleBundle",
    "ProceduralParticleEmitterState",
    "ProceduralParticleRenderSystem",
    "ProceduralParticleSimulationSystem",
    "RenderOverlay",
    "SceneCaptureConfig",
    "PaddleBouncePolicy",
    "POTION_ALPHA_RAMP",
    "POTION_COLOR_RAMP",
    "POTION_PARTICLE_PROFILE",
    "SMOKE_COLOR_RAMP",
    "SMOKE_PARTICLE_PROFILE",
    "SMOKE_ALPHA_RAMP",
    "SpawnBinding",
    "SpawnSystem",
    "AxisIntentBinding",
    "ViewportConstraintBinding",
    "ViewportConstraintSystem",
    "WaveProgressionBinding",
    "WaveProgressionSystem",
    "action_map_from_bindings_config",
    "action_map_from_controls_config",
    "action_map_from_scene_capture_config",
    "apply_bounce_hit",
    "arena_tile_map_from_strings",
    "available_directions",
    "blast_cells",
    "block_cells_from_strings",
    "choose_first_grid_cell",
    "fire_particle_binding",
    "free_grid_cells",
    "magic_particle_binding",
    "is_walkable_arena_tile",
    "is_junction",
    "occupied_grid_cells",
    "particle_binding_with_profile",
    "piece_fits",
    "potion_particle_binding",
    "reflect_from_viewport",
    "resolve_rect_bounce",
    "smoke_particle_binding",
    "spawn_explosion_from_bomb",
    "step_in_direction",
    "tile_map_from_strings",
    "ProceduralParticleProfile",
    "TileMap",
    "TimedMode",
    "TunnelWrapBinding",
    "TunnelWrapSystem",
    "ViewportBounceBinding",
    "ViewportBounceSystem",
]
