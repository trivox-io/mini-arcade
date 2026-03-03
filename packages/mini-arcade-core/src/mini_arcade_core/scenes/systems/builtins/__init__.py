"""
Built-in systems for scenes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar

from mini_arcade_core.engine.entities import BaseEntity
from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.scenes.sim_scene import (
    BaseIntent,
    BaseTickContext,
    BaseWorld,
    DrawCall,
    Layer,
    RenderQueue,
    SubmitRenderQueue,
)
from mini_arcade_core.scenes.systems.base_system import (
    BaseSystem,
)
from mini_arcade_core.spaces.math.vec2 import Vec2

from .actions import (  # noqa: E402  (re-export)
    ActionIntentSystem,
    ActionMap,
    ActionSnapshot,
    AxisActionBinding,
    DigitalActionBinding,
)
from .capture_hotkeys import (  # noqa: E402  (re-export)
    CaptureHotkeysConfig,
    CaptureHotkeysSystem,
)


class RenderSystemContext(Protocol):
    """
    Structural context contract for render systems.

    Any scene tick context that provides these attributes will be accepted.
    """

    world: BaseWorld
    draw_ops: list[DrawCall] | None
    render_queue: RenderQueue
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
    # phase: int = 10
    order: int = 10

    def build_intent(self, ctx: BaseTickContext) -> BaseIntent:
        """Build the intent"""
        raise NotImplementedError

    def step(self, ctx: BaseTickContext):
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
    order: int = 100

    def build_draw_ops(self, ctx: TTickContext) -> list[DrawCall]:
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

    def emit(self, ctx: TTickContext, rq: RenderQueue) -> None:
        """
        Emit draw calls into the render queue.

        :param ctx: The tick context containing world state and other info.
        :type ctx: BaseTickContext
        :param rq: The render queue to emit draw calls into.
        :type rq: RenderQueue
        """

        for entity in ctx.world.entities or []:
            self.emit_entity(ctx, rq, entity)

    # pylint: disable=too-many-locals
    def emit_entity(
        self, _ctx: TTickContext, rq: RenderQueue, entity: BaseEntity
    ) -> None:
        """
        Emit a single entity into the render queue.

        Subclasses can override this hook for entity-specific rendering,
        then delegate back to ``super().emit_entity`` for default behavior.
        """
        t = entity.transform
        shape = entity.shape
        z = entity.z_index
        color = (
            entity.style.fill
            if entity.style and entity.style.fill
            else (255, 255, 255, 255)
        )

        # Component-driven rendering: anim/sprite first, shape fallback.
        if entity.anim is not None and entity.anim.texture is not None:
            rq.texture(
                tex_id=entity.anim.texture,
                x=t.center.x,
                y=t.center.y,
                w=t.size.width,
                h=t.size.height,
                angle_deg=float(getattr(entity, "rotation_deg", 0.0)),
                layer="world",
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
                angle_deg=float(getattr(entity, "rotation_deg", 0.0)),
                layer="world",
                z=z,
            )
            return

        if shape.kind == "rect":
            rq.rect(
                center=t.center,
                size=t.size,
                color=color,
                layer="world",
                z=z,
            )

        elif shape.kind == "line":
            a = Vec2(t.center.x + shape.a.x, t.center.y + shape.a.y)
            b = Vec2(t.center.x + shape.b.x, t.center.y + shape.b.y)
            thickness = (
                entity.style.stroke.get("thickness", 1.0)
                if entity.style and entity.style.stroke
                else 1.0
            )
            color = (
                entity.style.stroke.get("color", color)
                if entity.style and entity.style.stroke
                else color
            )
            rq.line(
                a=a,
                b=b,
                color=color,
                thickness=thickness,
                dash_length=getattr(shape, "dash_length", None),
                dash_gap=getattr(shape, "dash_gap", None),
                layer="world",
                z=z,
            )

        elif shape.kind == "circle":
            # keep consistent with your current "center is position" usage:
            r = shape.radius or (min(t.size.width, t.size.height) * 0.5)
            rq.circle(
                center=Vec2(t.center.x + r, t.center.y + r),
                radius=r,
                color=color,
                layer="world",
                z=z,
            )

        elif shape.kind == "triangle":
            x, y = (
                t.center.x,
                t.center.y,
            )  # actually top-left in your current engine
            w, h = t.size.width, t.size.height

            points = [
                Vec2(x + w * 0.5, y),  # top middle
                Vec2(x, y + h),  # bottom left
                Vec2(x + w, y + h),  # bottom right
            ]

            rq.poly(
                points=points,
                fill=color,
                stroke=None,
                thickness=0,
                closed=True,
                layer="world",
                z=z,
            )

        elif shape.kind == "poly" and shape.points:
            ox = t.center.x + (t.size.width * 0.5)
            oy = t.center.y + (t.size.height * 0.5)

            points = [Vec2(ox + p.x, oy + p.y) for p in shape.points]

            rq.poly(
                points=points,
                fill=color,
                stroke=None,
                thickness=0,
                closed=True,
                layer="world",
                z=z,
            )

    def build_draw_ops(self, ctx: TTickContext) -> list[DrawCall]:
        rq = ctx.render_queue
        rq.clear()
        self.emit(ctx, rq)
        queued_ops = [DrawCall(SubmitRenderQueue(), ctx)]
        if not self.merge_existing_draw_ops:
            return queued_ops

        extra_ops = list(ctx.draw_ops or [])
        # Render queue first, then additional DrawCall-based overlays.
        return [*queued_ops, *extra_ops]

    @staticmethod
    def _build_pass_ops(ctx: TTickContext) -> dict[str, tuple[DrawCall, ...]]:
        layer_map: dict[str, tuple[Layer, ...]] = {
            "world": ("world", "debug"),
            "lighting": ("lighting",),
            "ui": ("ui",),
            "effects": ("effects", "postfx"),
        }
        out: dict[str, tuple[DrawCall, ...]] = {}
        for pass_name, layers in layer_map.items():
            if not ctx.render_queue.iter_sorted(layers):
                continue
            out[pass_name] = (DrawCall(SubmitRenderQueue(layers=layers), ctx),)
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
