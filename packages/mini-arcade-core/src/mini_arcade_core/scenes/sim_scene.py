"""
Simulation scene protocol module.
Defines the SimScene protocol for simulation scenes.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Generic, Literal, Type, TypeVar

from mini_arcade_core.backend.backend import Backend
from mini_arcade_core.backend.types import Color
from mini_arcade_core.engine.entities import BaseEntity
from mini_arcade_core.engine.render.packet import DrawOp, RenderPacket
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.systems.system_pipeline import SystemPipeline
from mini_arcade_core.spaces.math.vec2 import Vec2

if TYPE_CHECKING:
    from mini_arcade_core.engine.commands import CommandQueue

# pylint: disable=invalid-name
TWorld = TypeVar("TWorld")
TIntent = TypeVar("TIntent")
TContext = TypeVar("TContext", bound="BaseTickContext")
# pylint: enable=invalid-name


@dataclass
class BaseWorld:
    """
    Base type for scene world state.

    The world is the single object that represents *everything the scene owns*:
    - gameplay state (entities, score, cooldowns, flags)
    - simulation variables (timers, direction, RNG state if needed)
    - cached runtime resources (texture ids, sound ids, animations)
    - debug/UI overlay state

    Define one world dataclass per scene by inheriting from this class.
    The engine will create it during scene init and provide it to systems each tick.
    """

    entities: list[BaseEntity]

    def get_entity_by_id(self, entity_id: int) -> BaseEntity | None:
        """
        Get an entity by its ID.

        :param entity_id: The ID of the entity to retrieve.
        :type entity_id: int
        :return: The entity with the specified ID, or None if not found.
        :rtype: BaseEntity | None
        """
        for entity in self.entities:
            if entity.id == entity_id:
                return entity
        return None

    def get_entities_by_id_range(
        self, start_id: int, end_id: int
    ) -> list[BaseEntity]:
        """
        Get entities with IDs in the specified range [start_id, end_id].

        :param start_id: The starting ID of the range (inclusive).
        :type start_id: int
        :param end_id: The ending ID of the range (inclusive).
        :type end_id: int
        :return: A list of entities with IDs in the specified range.
        :rtype: list[BaseEntity]
        """
        return [
            entity
            for entity in self.entities
            if start_id <= entity.id <= end_id
        ]


class BaseIntent:
    """
    Base type for scene intent.

    Intent is a per-frame snapshot produced by the input layer and consumed by
    simulation systems. It should:
    - be independent from raw device events (keyboard/gamepad/mouse)
    - use normalized values (e.g. axis -1..+1, booleans for actions)
    - represent desired actions for *this tick only* (not persistent state)

    Scenes define their own intent dataclass inheriting from this base.
    """


class Drawable(ABC, Generic[TContext]):
    """
    A drawable for scenes that can be drawn.
    """

    @abstractmethod
    def draw(self, backend: Backend, ctx: TContext):
        """
        Draw to the scene.
        """
        raise NotImplementedError


@dataclass(frozen=True)
class DrawCall:
    """
    A draw call for rendering.
    """

    drawable: Drawable[TContext]
    ctx: TContext

    def __call__(self, backend: Backend) -> None:
        self.drawable.draw(backend, self.ctx)


Layer = Literal["world", "lighting", "ui", "effects", "postfx", "debug"]
OperationKind = Literal[
    "draw_rect",
    "draw_circle",
    "draw_line",
    "draw_texture",
    "draw_text",
    "draw_poly",
    "custom",
]

_LAYER_ORDER: dict[Layer, int] = {
    "world": 0,
    "lighting": 1,
    "ui": 2,
    "effects": 3,
    "postfx": 3,
    "debug": 4,
}


@dataclass
class DrawOperation:
    """
    A draw operation for rendering.
    """

    kind: OperationKind
    layer: Layer
    z: int = 0  # for sorting within layer
    seq: int = 0  # for stable sorting of ops with same layer/z
    payload: object | None = None  # operation-specific data


@dataclass
class RenderQueue:

    _ops: list[DrawOperation] = field(default_factory=list)
    _seq: int = 0

    def clear(self) -> None:
        self._ops.clear()
        self._seq = 0

    def _push(
        self, kind: OperationKind, layer: Layer, z: int, payload: object
    ) -> None:
        self._ops.append(
            DrawOperation(
                kind=kind, layer=layer, z=z, seq=self._seq, payload=payload
            )
        )
        self._seq += 1

    # helpers
    def rect(
        self,
        *,
        center,
        size,
        color,
        radius=0.0,
        layer: Layer = "world",
        z: int = 0,
    ) -> None:
        self._push("draw_rect", layer, z, (center, size, color, radius))

    def line(
        self,
        *,
        a,
        b,
        color,
        thickness=1.0,
        dash_length: float | None = None,
        dash_gap: float | None = None,
        layer: Layer = "world",
        z: int = 0,
    ) -> None:
        self._push(
            "draw_line",
            layer,
            z,
            (a, b, color, thickness, dash_length, dash_gap),
        )

    def circle(
        self,
        *,
        center,
        radius,
        color,
        layer: Layer = "world",
        z: int = 0,
    ) -> None:
        self._push("draw_circle", layer, z, (center, radius, color))

    def poly(
        self,
        *,
        points: list[Vec2],
        fill: Color | None,
        stroke: Color | None,
        thickness: int = 1,
        closed: bool = True,
        layer: Layer = "world",
        z: int = 0,
    ) -> None:
        self._push(
            "draw_poly", layer, z, (points, fill, stroke, thickness, closed)
        )

    def texture(
        self,
        *,
        tex_id: int,
        x: float,
        y: float,
        w: float,
        h: float,
        angle_deg: float = 0.0,
        layer: Layer = "world",
        z: int = 0,
    ) -> None:
        self._push("draw_texture", layer, z, (tex_id, x, y, w, h, angle_deg))

    def text(
        self,
        *,
        x: float,
        y: float,
        text: str,
        color: Color = (255, 255, 255, 255),
        font_size: int | None = None,
        align: Literal["left", "center", "right"] = "left",
        layer: Layer = "ui",
        z: int = 0,
    ) -> None:
        self._push(
            "draw_text",
            layer,
            z,
            (x, y, text, color, font_size, align),
        )

    def custom(
        self,
        *,
        op: Callable[[Backend], None],
        layer: Layer = "debug",
        z: int = 0,
    ) -> None:
        self._push("custom", layer, z, op)

    def iter_sorted(
        self, layers: tuple[Layer, ...] | list[Layer] | None = None
    ) -> list[DrawOperation]:
        if layers is None:
            ops = self._ops
        else:
            wanted = set(layers)
            ops = [op for op in self._ops if op.layer in wanted]
        return sorted(ops, key=lambda o: (_LAYER_ORDER[o.layer], o.z, o.seq))


@dataclass
class BaseTickContext(Generic[TWorld, TIntent]):
    """
    Per-tick execution context passed through a SimScene pipeline.

    This is the "shared envelope" for one simulation tick: input snapshot + timing,
    the mutable world state, an outbox for commands, and the per-tick intent and
    render output produced by systems.

    :ivar input_frame: Snapshot of raw/normalized input for this tick.
    :ivar dt: Delta time (seconds) since previous tick.
    :ivar world: Scene-owned world state (usually mutated during the tick).
    :ivar commands: Queue of commands/events emitted by systems.
    :ivar intent: Optional intent snapshot for this tick (produced by input system).
    :ivar packet: Optional render packet produced for this tick.
    :ivar draw_ops: Optional immediate draw operations (debug/overlay/utility).
    """

    input_frame: InputFrame
    dt: float
    world: TWorld
    commands: CommandQueue
    intent: TIntent | None = None
    packet: RenderPacket | None = None
    draw_ops: list[DrawOp] | None = None
    render_queue: RenderQueue = field(default_factory=RenderQueue)


@dataclass(frozen=True)
class SubmitRenderQueue(Drawable[BaseTickContext]):
    layers: tuple[Layer, ...] | None = None

    @staticmethod
    def _draw_line(
        backend: Backend,
        *,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        color: Color,
        thickness: float,
    ) -> None:
        try:
            th = max(1, int(round(thickness)))
            backend.render.draw_line(x1, y1, x2, y2, color=color, thickness=th)
        except TypeError:
            backend.render.draw_line(x1, y1, x2, y2, color=color)

    @classmethod
    def _draw_dashed_line(
        cls,
        backend: Backend,
        *,
        a: Vec2,
        b: Vec2,
        color: Color,
        thickness: float,
        dash_length: float,
        dash_gap: float,
    ) -> None:
        dx = b.x - a.x
        dy = b.y - a.y
        dist = math.hypot(dx, dy)
        if dist <= 0.0:
            return

        if dash_length <= 0.0 or dash_gap <= 0.0:
            cls._draw_line(
                backend,
                x1=a.x,
                y1=a.y,
                x2=b.x,
                y2=b.y,
                color=color,
                thickness=thickness,
            )
            return

        step = dash_length + dash_gap
        traveled = 0.0
        while traveled < dist:
            seg_start = traveled / dist
            seg_end = min(traveled + dash_length, dist) / dist
            cls._draw_line(
                backend,
                x1=a.x + (dx * seg_start),
                y1=a.y + (dy * seg_start),
                x2=a.x + (dx * seg_end),
                y2=a.y + (dy * seg_end),
                color=color,
                thickness=thickness,
            )
            traveled += step

    def draw(self, backend: Backend, ctx: BaseTickContext):
        rq = ctx.render_queue
        for op in rq.iter_sorted(self.layers):

            if op.kind == "draw_rect":
                center, size, color, radius = op.payload
                backend.render.draw_rect(
                    center.x, center.y, size.width, size.height, color=color
                )

            elif op.kind == "draw_line":
                payload = op.payload
                if not isinstance(payload, tuple):
                    raise ValueError(
                        f"Unexpected draw_line payload: {payload!r}"
                    )

                if len(payload) == 6:
                    (
                        a,
                        b,
                        color,
                        thickness,
                        dash_length,
                        dash_gap,
                    ) = payload
                elif len(payload) == 4:
                    a, b, color, thickness = payload
                    dash_length = None
                    dash_gap = None
                else:
                    raise ValueError(
                        f"Unexpected draw_line payload: {payload!r}"
                    )

                # Try the “new” signature first, fallback to the old one.
                if dash_length is not None and dash_gap is not None:
                    self._draw_dashed_line(
                        backend,
                        a=a,
                        b=b,
                        color=color,
                        thickness=thickness,
                        dash_length=float(dash_length),
                        dash_gap=float(dash_gap),
                    )
                else:
                    self._draw_line(
                        backend,
                        x1=a.x,
                        y1=a.y,
                        x2=b.x,
                        y2=b.y,
                        color=color,
                        thickness=float(thickness),
                    )

            elif op.kind == "draw_circle":
                center, radius, color = op.payload
                backend.render.draw_circle(
                    int(center.x), int(center.y), int(radius), color=color
                )

            elif op.kind == "draw_texture":
                tex_id, x, y, w, h, angle_deg = op.payload
                backend.render.draw_texture(
                    int(tex_id),
                    int(x),
                    int(y),
                    int(w),
                    int(h),
                    float(angle_deg),
                )

            elif op.kind == "draw_text":
                x, y, text, color, font_size, align = op.payload
                draw_x = int(x)
                draw_y = int(y)

                if align in ("center", "right"):
                    text_w, _ = backend.text.measure(
                        str(text),
                        font_size=(
                            int(font_size) if font_size is not None else None
                        ),
                    )
                    if align == "center":
                        draw_x -= text_w // 2
                    else:
                        draw_x -= text_w

                backend.text.draw(
                    draw_x,
                    draw_y,
                    str(text),
                    color=color,
                    font_size=(
                        int(font_size) if font_size is not None else None
                    ),
                )

            elif op.kind == "draw_poly":
                payload = op.payload
                if payload is None:
                    continue

                # Support both:
                #   old: (points, color, filled)
                #   new: (points, fill, stroke, thickness, closed)
                if isinstance(payload, tuple) and len(payload) == 3:
                    points, color, filled = payload
                    closed = True
                elif isinstance(payload, tuple) and len(payload) == 5:
                    points, fill, _stroke, _thickness, closed = payload
                    color = fill if fill is not None else (255, 255, 255, 255)
                    filled = fill is not None
                else:
                    raise ValueError(
                        f"Unexpected draw_poly payload: {payload!r}"
                    )

                pts = [(int(p.x), int(p.y)) for p in points]

                if not closed:
                    # polyline (not a polygon)
                    for i in range(len(pts) - 1):
                        (x1, y1) = pts[i]
                        (x2, y2) = pts[i + 1]
                        backend.render.draw_line(x1, y1, x2, y2, color=color)
                else:
                    backend.render.draw_poly(pts, color=color, filled=filled)

            elif op.kind == "custom":
                payload = op.payload
                if callable(payload):
                    payload(backend)


@dataclass
class SimScene(Generic[TContext, TWorld]):
    """
    Simulation-first scene base.

    Lifecycle:
      - __init__(RuntimeContext): constructs the scene container
      - on_enter(): allocate resources, build world, register systems
      - tick(input_frame, dt): build per-tick context, run systems, return RenderPacket

    Subclasses typically provide:
      - build_pipeline() OR register systems in on_enter()
      - build_world() (often in on_enter when window size/assets are needed)

    :ivar context: RuntimeContext for this scene.
    :ivar systems: System pipeline
    :ivar world: Scene world, often set in on_enter
    :tick_context_type: Type of the tick context
    """

    context: RuntimeContext
    systems: SystemPipeline[TContext]
    world: TWorld

    # 👇 each scene sets this
    tick_context_type: Type[TContext] | None = None

    def __init__(self, ctx: RuntimeContext):
        self.context = ctx
        self.systems = self.build_pipeline()

    def build_pipeline(self) -> SystemPipeline[TContext]:
        """
        Return an empty pipeline by default; scenes can override.

        :return: Empty pipeline
        :rtype: SystemPipeline[TContext]
        """
        return SystemPipeline[TContext]()

    def make_world(self) -> TWorld: ...

    def on_enter(self):
        """Called when the scene becomes active (safe place to create world & add systems)."""

    def on_exit(self):
        """Called when the scene stops being active (cleanup optional)."""

    def _load_texture(self, path: str) -> int:
        return self.context.services.render.load_texture(path)

    def _get_tick_context(
        self, input_frame: InputFrame, dt: float
    ) -> TContext:
        """Construct the tick context for the current tick."""
        if self.tick_context_type is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} must set tick_context_type "
                "or override _get_tick_context()."
            )
        return self.tick_context_type(
            input_frame=input_frame,
            dt=dt,
            world=self.world,
            commands=self.context.command_queue,
        )

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        """
        Advance the simulation by dt seconds, processing input_frame.

        :param input_frame: Current input frame.
        :type input_frame: InputFrame

        :param dt: Delta time since last tick.
        :type dt: float
        """
        ctx = self._get_tick_context(input_frame, dt)
        self.systems.step(ctx)

        if ctx.packet is None:
            raise RuntimeError(
                f"{self.__class__.__name__} produced no RenderPacket. "
                "Did you forget to add a render system that sets ctx.packet?"
            )
        return ctx.packet
