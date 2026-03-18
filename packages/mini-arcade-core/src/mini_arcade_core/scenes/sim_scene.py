"""
Simulation scene protocol module.
Defines the SimScene protocol for simulation scenes.
"""

# pylint: disable=too-many-lines

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Callable,
    ClassVar,
    Generic,
    Iterable,
    Literal,
    Type,
    TypeVar,
)

from mini_arcade_core.backend.backend import Backend
from mini_arcade_core.backend.types import Color
from mini_arcade_core.engine.commands import (
    ChangeSceneCommand,
    PopSceneCommand,
    PushSceneCommand,
    PushSceneIfMissingCommand,
    QuitCommand,
    RemoveSceneCommand,
)
from mini_arcade_core.engine.entities import BaseEntity
from mini_arcade_core.engine.render.packet import DrawOp, RenderPacket
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.systems.builtins.capture_hotkeys import (
    CaptureHotkeysConfig,
    CaptureHotkeysSystem,
    SceneCaptureConfig,
    action_map_from_scene_capture_config,
)
from mini_arcade_core.scenes.systems.system_pipeline import SystemPipeline
from mini_arcade_core.spaces.math.vec2 import Vec2

if TYPE_CHECKING:
    from mini_arcade_core.engine.commands import CommandQueue

# pylint: disable=invalid-name
TWorld = TypeVar("TWorld")
TIntent = TypeVar("TIntent")
TContext = TypeVar("TContext", bound="BaseTickContext")
# pylint: enable=invalid-name


@dataclass(frozen=True)
class EntityIdDomain:
    """
    Named entity-id allocation domain.
    """

    start_id: int
    end_id: int


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

    entity_id_domains: ClassVar[dict[str, EntityIdDomain]] = {}
    entities: list[BaseEntity]
    _entities_by_id: dict[int, BaseEntity] = field(
        init=False, default_factory=dict, repr=False
    )
    _entities_by_tag: dict[str, list[BaseEntity]] = field(
        init=False, default_factory=dict, repr=False
    )
    _entities_by_range: dict[tuple[int, int], list[BaseEntity]] = field(
        init=False, default_factory=dict, repr=False
    )

    def __setattr__(self, name: str, value: object) -> None:
        if name == "entities" and isinstance(value, list):
            if not isinstance(value, _TrackedEntityList):
                value = _TrackedEntityList(self, value)
        super().__setattr__(name, value)
        if name == "entities" and hasattr(self, "_entities_by_id"):
            self._rebuild_entity_indexes()

    def __post_init__(self) -> None:
        self.entities = list(self.entities)
        self._rebuild_entity_indexes()

    def _rebuild_entity_indexes(self) -> None:
        self._entities_by_id = {}
        self._entities_by_tag = {}
        for entity in list(self.entities):
            self._entities_by_id[int(entity.id)] = entity
            for raw_tag in getattr(entity, "tags", ()) or ():
                tag = str(raw_tag).strip().lower()
                if not tag:
                    continue
                self._entities_by_tag.setdefault(tag, []).append(entity)
        self._entities_by_range.clear()

    def get_entity_by_id(self, entity_id: int) -> BaseEntity | None:
        """
        Get an entity by its ID.

        :param entity_id: The ID of the entity to retrieve.
        :type entity_id: int
        :return: The entity with the specified ID, or None if not found.
        :rtype: BaseEntity | None
        """
        return self._entities_by_id.get(int(entity_id))

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
        cache_key = (int(start_id), int(end_id))
        cached = self._entities_by_range.get(cache_key)
        if cached is not None:
            return cached

        entities = [
            entity
            for entity in self.entities
            if cache_key[0] <= int(entity.id) <= cache_key[1]
        ]
        self._entities_by_range[cache_key] = entities
        return entities

    def get_entities_by_tag(self, tag: str) -> list[BaseEntity]:
        """
        Get entities registered with a normalized tag.
        """
        normalized = str(tag).strip().lower()
        if not normalized:
            return []
        return list(self._entities_by_tag.get(normalized, ()))

    @classmethod
    def entity_id_domain(cls, domain_name: str) -> EntityIdDomain:
        """
        Resolve a named entity-id domain declared by the world class.
        """
        normalized = str(domain_name).strip().lower()
        domain = cls.entity_id_domains.get(normalized)
        if domain is None:
            raise KeyError(
                f"{cls.__name__} has no entity-id domain named "
                f"{domain_name!r}"
            )
        return domain

    def get_entities_in_domain(self, domain_name: str) -> list[BaseEntity]:
        """
        Return entities within a named entity-id domain.
        """
        domain = self.entity_id_domain(domain_name)
        return self.get_entities_by_id_range(domain.start_id, domain.end_id)

    def allocate_entity_id(
        self,
        start_id: int,
        end_id: int,
        *,
        reserved_ids: Iterable[int] | None = None,
    ) -> int | None:
        """
        Allocate the first free entity id within [start_id, end_id].
        """
        start = int(start_id)
        end = int(end_id)
        used = {
            int(entity.id)
            for entity in self.get_entities_by_id_range(start, end)
        }
        if reserved_ids is not None:
            used.update(
                int(entity_id)
                for entity_id in reserved_ids
                if start <= int(entity_id) <= end
            )
        for candidate in range(start, end + 1):
            if candidate not in used:
                return candidate
        return None

    def allocate_entity_id_for(
        self,
        domain_name: str,
        *,
        reserved_ids: Iterable[int] | None = None,
    ) -> int | None:
        """
        Allocate the first free entity id inside a named domain.
        """
        domain = self.entity_id_domain(domain_name)
        return self.allocate_entity_id(
            domain.start_id,
            domain.end_id,
            reserved_ids=reserved_ids,
        )

    def remove_entities_by_ids(self, entity_ids: Iterable[int]) -> None:
        """
        Remove all entities whose ids match the provided iterable.
        """
        ids = {int(entity_id) for entity_id in entity_ids}
        if not ids:
            return
        self.entities = [
            entity for entity in self.entities if int(entity.id) not in ids
        ]

    def compact_tracked_entity_ids(
        self,
        *,
        attr_name: str,
        start_id: int,
        end_id: int,
        keep_entity: Callable[[BaseEntity], bool] | None = None,
    ) -> list[int]:
        """
        Compact a tracked id list and remove entities in the associated id
        window that no longer satisfy ``keep_entity``.
        """
        tracked = getattr(self, attr_name, []) or []
        keep_entity = keep_entity or (lambda _entity: True)
        kept_ids: list[int] = []
        kept_id_set: set[int] = set()

        for entity_id in tracked:
            normalized = int(entity_id)
            if normalized in kept_id_set:
                continue
            entity = self.get_entity_by_id(normalized)
            if entity is None or not keep_entity(entity):
                continue
            kept_ids.append(normalized)
            kept_id_set.add(normalized)

        setattr(self, attr_name, kept_ids)

        stale_ids = {
            int(entity.id)
            for entity in self.get_entities_by_id_range(
                int(start_id), int(end_id)
            )
            if int(entity.id) not in kept_id_set
        }
        self.remove_entities_by_ids(stale_ids)
        return kept_ids

    def compact_tracked_entity_ids_for(
        self,
        *,
        attr_name: str,
        domain_name: str,
        keep_entity: Callable[[BaseEntity], bool] | None = None,
    ) -> list[int]:
        """
        Compact a tracked id list against a named entity-id domain.
        """
        domain = self.entity_id_domain(domain_name)
        return self.compact_tracked_entity_ids(
            attr_name=attr_name,
            start_id=domain.start_id,
            end_id=domain.end_id,
            keep_entity=keep_entity,
        )

    def find_entities(
        self,
        *,
        tag: str | None = None,
        entity_type: type[BaseEntity] | None = None,
        predicate: Callable[[BaseEntity], bool] | None = None,
    ) -> list[BaseEntity]:
        """
        Query entities by tag, type, and/or predicate.
        """
        if tag is not None:
            entities: Iterable[BaseEntity] = self.get_entities_by_tag(tag)
        else:
            entities = self.entities

        out: list[BaseEntity] = []
        for entity in entities:
            if entity_type is not None and not isinstance(entity, entity_type):
                continue
            if predicate is not None and not predicate(entity):
                continue
            out.append(entity)
        return out

    def find_entity(
        self,
        *,
        tag: str | None = None,
        entity_type: type[BaseEntity] | None = None,
        predicate: Callable[[BaseEntity], bool] | None = None,
    ) -> BaseEntity | None:
        """
        Return the first entity that matches the query.
        """
        matches = self.find_entities(
            tag=tag,
            entity_type=entity_type,
            predicate=predicate,
        )
        return matches[0] if matches else None


class _TrackedEntityList(list[BaseEntity]):
    """
    List wrapper that keeps BaseWorld indexes in sync after mutation.
    """

    def __init__(
        self,
        owner: BaseWorld,
        values: list[BaseEntity] | tuple[BaseEntity, ...],
    ):
        self._owner = owner
        super().__init__(values)

    def _did_change(self) -> None:
        self._owner._rebuild_entity_indexes()  # pylint: disable=protected-access

    def append(self, item: BaseEntity) -> None:
        super().append(item)
        self._did_change()

    def extend(self, values) -> None:
        super().extend(values)
        self._did_change()

    def insert(self, index: int, item: BaseEntity) -> None:
        super().insert(index, item)
        self._did_change()

    def pop(self, index: int = -1):
        item = super().pop(index)
        self._did_change()
        return item

    def remove(self, item: BaseEntity) -> None:
        super().remove(item)
        self._did_change()

    def clear(self) -> None:
        super().clear()
        self._did_change()

    def __delitem__(self, index) -> None:
        super().__delitem__(index)
        self._did_change()

    def __setitem__(self, index, value) -> None:
        super().__setitem__(index, value)
        self._did_change()

    def __iadd__(self, values):
        result = super().__iadd__(values)
        self._did_change()
        return result

    def sort(self, *, key=None, reverse: bool = False) -> None:
        super().sort(key=key, reverse=reverse)
        self._did_change()

    def reverse(self) -> None:
        super().reverse()
        self._did_change()


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
    """
    A queue of draw operations to be rendered this tick.
    Scenes/systems can push draw operations to this queue during the tick,
    and the engine will sort and render them after the tick.
    This is a more flexible alternative to building a full RenderPacket for simple
    scenes that just want to emit draw calls.
    """

    _ops: list[DrawOperation] = field(default_factory=list)
    _seq: int = 0

    def clear(self) -> None:
        """
        Clear all draw operations from the queue.
        """
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
    # pylint: disable=too-many-arguments
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
        """
        Push a rectangle draw operation.

        :param center: Center position of the rectangle.
        :type center: Vec2
        :param size: Size of the rectangle (width, height).
        :type size: Vec2
        :param color: Color of the rectangle.
        :type color: Color
        :param radius: Optional corner radius for rounded rectangles (default 0).
        :type radius: float
        :param layer: The layer to draw on (default "world").
        :type layer: Layer
        :param z: The z-index for sorting within the layer (default 0).
        :type z: int
        """
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
        """
        Push a line draw operation, with optional dashed line parameters.

        :param a: Starting point of the line.
        :type a: Vec2
        :param b: Ending point of the line.
        :type b: Vec2
        :param color: Color of the line.
        :type color: Color
        :param thickness: Thickness of the line (default 1.0).
        :type thickness: float
        :param dash_length: Length of dashes for dashed line (None for solid line).
        :type dash_length: float | None
        :param dash_gap: Length of gaps for dashed line (None for solid line).
        :type dash_gap: float | None
        :param layer: The layer to draw on (default "world").
        :type layer: Layer
        :param z: The z-index for sorting within the layer (default 0).
        :type z: int
        """
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
        """
        Push a circle draw operation.

        :param center: Center position of the circle.
        :type center: Vec2
        :param radius: Radius of the circle.
        :type radius: float
        :param color: Color of the circle.
        :type color: Color
        :param layer: The layer to draw on (default "world").
        :type layer: Layer
        :param z: The z-index for sorting within the layer (default 0).
        :type z: int
        """
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
        """
        Push a polygon draw operation.

        :param points: List of points defining the polygon vertices.
        :type points: list[Vec2]
        :param fill: Fill color for the polygon (None for no fill).
        :type fill: Color | None
        :param stroke: Stroke color for the polygon edges (None for no stroke).
        :type stroke: Color | None
        :param thickness: Thickness of the stroke (default 1).
        :type thickness: int
        :param closed: Whether the polygon should be closed (default True).
        :type closed: bool
        :param layer: The layer to draw on (default "world").
        :type layer: Layer
        :param z: The z-index for sorting within the layer (default 0).
        :type z: int
        """
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
        """
        Push a texture draw operation.

        :param tex_id: The texture ID to draw.
        :type tex_id: int
        :param x: X position to draw the texture.
        :type x: float
        :param y: Y position to draw the texture.
        :type y: float
        :param w: Width to draw the texture.
        :type w: float
        :param h: Height to draw the texture.
        :type h: float
        :param angle_deg: Rotation angle in degrees (default 0).
        :type angle_deg: float
        :param layer: The layer to draw on (default "world").
        :type layer: Layer
        :param z: The z-index for sorting within the layer (default 0).
        :type z: int
        """
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
        """
        Push a text draw operation.

        :param x: X position of the text.
        :type x: float
        :param y: Y position of the text.
        :type y: float
        :param text: The text string to draw.
        :type text: str
        :param color: The color of the text (default white).
        :type color: Color
        :param font_size: Optional font size (default None for backend default).
        :type font_size: int | None
        :param align: Text alignment: "left", "center", or "right" (default "left").
        :type align: Literal["left", "center", "right"]
        :param layer: The layer to draw on (default "ui").
        :type layer: Layer
        :param z: The z-index for sorting within the layer (default 0).
        :type z: int
        """
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
        """
        Push a custom draw operation defined by a callable that takes the backend.

        :param op: A callable that takes a Backend and performs custom drawing.
        :type op: Callable[[Backend], None]
        :param layer: The layer to draw on (default "debug").
        :type layer: Layer
        :param z: The z-index for sorting within the layer (default 0).
        :type z: int
        """
        self._push("custom", layer, z, op)

    def iter_sorted(
        self, layers: tuple[Layer, ...] | list[Layer] | None = None
    ) -> list[DrawOperation]:
        """
        Get draw operations sorted by layer/z/seq, optionally filtered by layers.

        :param layers: Optional tuple or list of layers to include (default all).
        :type layers: tuple[Layer, ...] | list[Layer] | None
        :return: Sorted list of draw operations for the specified layers.
        :rtype: list[DrawOperation]
        """
        if layers is None:
            ops = self._ops
        else:
            wanted = set(layers)
            ops = [op for op in self._ops if op.layer in wanted]
        return sorted(ops, key=lambda o: (_LAYER_ORDER[o.layer], o.z, o.seq))


# pylint: disable=too-many-instance-attributes
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
    :ivar intent_channels: Optional per-source intent snapshots for this tick.
    :ivar packet: Optional render packet produced for this tick.
    :ivar draw_ops: Optional immediate draw operations (debug/overlay/utility).
    """

    input_frame: InputFrame
    dt: float
    world: TWorld
    commands: CommandQueue
    intent: TIntent | None = None
    intent_channels: dict[str, object] = field(default_factory=dict)
    packet: RenderPacket | None = None
    draw_ops: list[DrawOp] | None = None
    render_queue: RenderQueue = field(default_factory=RenderQueue)

    def intent_for(
        self, channel: str, default: object | None = None
    ) -> object:
        """
        Return the intent stored for a channel, if present.
        """
        return self.intent_channels.get(channel, default)


@dataclass(frozen=True)
class SubmitRenderQueue(Drawable[BaseTickContext]):
    """
    Drawable that submits a RenderQueue from the tick context.
    This is a utility for simple scenes that want to build a RenderQueue directly
    in their tick context and have it rendered without needing a full RenderPacket.

    :ivar layers: (tuple[Layer, ...] | None): Optional tuple of layers to
        render from the RenderQueue (default all).
    """

    layers: tuple[Layer, ...] | None = None

    @staticmethod
    # pylint: disable=too-many-arguments
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

    # pylint: disable=too-many-arguments
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

    # TODO: Refactor this method later.
    # Justification: This method is a bit long but it's mostly parsing the draw operations
    # and dispatching them, hard to break down more without overcomplicating it.
    # pylint: disable=too-many-branches,too-many-statements,too-many-locals
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
                    points, fill, stroke, _thickness, closed = payload
                    if fill is not None:
                        color = fill
                        filled = True
                    elif stroke is not None:
                        color = stroke
                        filled = False
                    else:
                        color = (255, 255, 255, 255)
                        filled = False
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
    capture_config: ClassVar[SceneCaptureConfig] = SceneCaptureConfig()

    # 👇 each scene sets this
    tick_context_type: Type[TContext] | None = None

    def __init__(self, ctx: RuntimeContext):
        self.context = ctx
        self.systems = self.build_pipeline()
        self.scene_id: str | None = None
        self._capture_controls_installed = False

    def build_pipeline(self) -> SystemPipeline[TContext]:
        """
        Return an empty pipeline by default; scenes can override.

        :return: Empty pipeline
        :rtype: SystemPipeline[TContext]
        """
        return SystemPipeline[TContext]()

    def on_enter(self):
        """Called when the scene becomes active (safe place to create world & add systems)."""

    def on_exit(self):
        """Called when the scene stops being active (cleanup optional)."""

    def debug_overlay_lines(self) -> list[str]:
        """
        Optional extension hook for the built-in debug overlay.

        Scenes can override this to expose scene-specific diagnostics.
        """
        return []

    def uses_builtin_escape_handling(self) -> bool:
        """
        Whether engine-level ESC handling should apply to this scene.
        """
        return True

    # pylint: disable=too-many-return-statements
    def configured_escape_command(self):
        """
        Resolve the configured ESC command for this scene, if any.
        """
        cfg = self.scene_runtime_settings()
        if cfg is None or cfg.escape is None:
            return None

        action = cfg.escape
        command = str(action.command).strip().lower()
        current_scene = self._resolve_scene_id()
        target_scene = (
            str(action.scene_id).strip() if action.scene_id is not None else ""
        )
        if command == "quit":
            return QuitCommand()
        if command == "pop_scene":
            return PopSceneCommand()
        if command == "remove_scene":
            return RemoveSceneCommand(target_scene or current_scene)
        if command == "change_scene" and target_scene:
            return ChangeSceneCommand(target_scene)
        if command == "push_scene" and target_scene:
            return PushSceneCommand(
                target_scene, as_overlay=bool(action.as_overlay)
            )
        if command == "push_scene_if_missing" and target_scene:
            return PushSceneIfMissingCommand(
                target_scene, as_overlay=bool(action.as_overlay)
            )
        return None

    def scene_runtime_settings(self):
        """
        Resolve per-scene gameplay config from runtime settings.
        """
        scene_settings = getattr(self.context.settings, "scene_settings", None)
        if not callable(scene_settings):
            return None
        return scene_settings(self._resolve_scene_id())

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

    def _resolve_scene_id(self) -> str:
        if self.scene_id:
            return str(self.scene_id)
        return self.__class__.__name__.lower()

    def _ensure_capture_controls(self) -> None:
        if self._capture_controls_installed:
            return

        cfg = self.capture_config.with_scene_defaults(self._resolve_scene_id())
        if cfg.any_enabled():
            hotkeys_cfg = CaptureHotkeysConfig.from_scene_capture_config(cfg)
            self.systems.add(
                CaptureHotkeysSystem(
                    services=self.context.services,
                    action_map=action_map_from_scene_capture_config(
                        cfg, hotkeys_cfg=hotkeys_cfg
                    ),
                    cfg=hotkeys_cfg,
                )
            )
        self._capture_controls_installed = True

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        """
        Advance the simulation by dt seconds, processing input_frame.

        :param input_frame: Current input frame.
        :type input_frame: InputFrame

        :param dt: Delta time since last tick.
        :type dt: float
        """
        self._ensure_capture_controls()
        ctx = self._get_tick_context(input_frame, dt)
        self.systems.step(ctx)

        if ctx.packet is None:
            raise RuntimeError(
                f"{self.__class__.__name__} produced no RenderPacket. "
                "Did you forget to add a render system that sets ctx.packet?"
            )
        return ctx.packet
