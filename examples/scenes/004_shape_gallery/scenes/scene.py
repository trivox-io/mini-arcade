"""
Minimal scene example with Debug Overlay (systems + draw_ops).
"""

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade.utils.logging import logger  # type: ignore[import-not-found]
from mini_arcade_core.backend.backend import Backend
from mini_arcade_core.scenes.autoreg import (
    register_scene,  # type: ignore[import-not-found]
)
from mini_arcade_core.scenes.sim_scene import (  # type: ignore[import-not-found]
    Drawable,
    SimScene,
)
from mini_arcade_core.scenes.systems.builtins import (  # type: ignore[import-not-found]
    BaseQueuedRenderSystem,
)
from mini_arcade_core.spaces.math.vec2 import Vec2

from ..entities import MyEntity
from .models import MinTickContext, MinWorld


class DrawShape(Drawable[MinTickContext]):
    """Drawable for our simple shape."""

    def draw(self, backend: Backend, ctx: MinTickContext):
        entities = ctx.world.entities or []
        logger.debug(f"Drawing {len(entities)} entities")
        for entity in entities:
            backend.render.draw_rect(
                entity.transform.center.x,
                entity.transform.center.y,
                entity.transform.size.width,
                entity.transform.size.height,
                color=(255, 0, 0),
            )


@dataclass
class MinRenderSystem(BaseQueuedRenderSystem):
    """Build draw_ops (world pass empty + overlay as UI pass)."""

    name: str = "min_render"
    order: int = 100

    # Justification: This example is outdated and will be replaced by a more comprehensive
    # one soon. It's not worth the effort to refactor it right now.
    # pylint: disable=too-many-locals
    def emit(self, ctx: MinTickContext, rq):
        for e in ctx.world.entities or []:
            t = e.transform
            shape = e.shape
            z = e.z_index

            if shape.kind == "rect":
                rq.rect(
                    center=t.center,
                    size=t.size,
                    color=(255, 0, 0, 255),
                    layer="world",
                    z=z,
                )

            elif shape.kind == "line":
                a = Vec2(t.center.x + shape.a.x, t.center.y + shape.a.y)
                b = Vec2(t.center.x + shape.b.x, t.center.y + shape.b.y)
                rq.line(
                    a=a,
                    b=b,
                    color=(255, 0, 0, 255),
                    thickness=1,
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
                    color=(255, 0, 0, 255),
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
                    fill=(255, 0, 0, 255),
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
                    fill=(255, 0, 0, 255),
                    stroke=None,
                    thickness=0,
                    closed=True,
                    layer="world",
                    z=z,
                )


# --------------------------------------------------------------------------------------
# Scene
# --------------------------------------------------------------------------------------
@register_scene("min")
class MinScene(SimScene[MinTickContext, MinWorld]):
    """
    Minimal scene that draws a debug overlay (scene name, backend name, FPS/frame time).
    """

    tick_context_type = MinTickContext

    def on_enter(self) -> None:
        self.world = MinWorld(
            entities=[
                MyEntity.from_dict(
                    {
                        "id": 1,
                        "name": "My Rectangle",
                        "transform": {
                            "center": {"x": 50.0, "y": 50.0},
                            "size": {"width": 25.0, "height": 25.0},
                        },
                        "shape": {
                            "kind": "rect",
                        },
                    }
                ),
                MyEntity.from_dict(
                    {
                        "id": 2,
                        "name": "My Line",
                        "transform": {
                            "center": {"x": 100.0, "y": 50.0},
                            "size": {"width": 25.0, "height": 25.0},
                        },
                        "shape": {
                            "kind": "line",
                            "a": {"x": 0.0, "y": 0.0},
                            "b": {"x": 25.0, "y": 25.0},
                        },
                    }
                ),
                MyEntity.from_dict(
                    {
                        "id": 3,
                        "name": "My Circle",
                        "transform": {
                            "center": {"x": 150.0, "y": 50.0},
                            "size": {"width": 25.0, "height": 25.0},
                        },
                        "shape": {
                            "kind": "circle",
                            "radius": 12.5,
                        },
                    }
                ),
                MyEntity.from_dict(
                    {
                        "id": 4,
                        "name": "My Triangle",
                        "transform": {
                            "center": {"x": 200.0, "y": 50.0},
                            "size": {"width": 25.0, "height": 25.0},
                        },
                        "shape": {
                            "kind": "triangle",
                        },
                    }
                ),
                MyEntity.from_dict(
                    {
                        "id": 5,
                        "name": "My Poly",
                        "transform": {
                            "center": {"x": 250.0, "y": 50.0},
                            "size": {"width": 25.0, "height": 25.0},
                        },
                        "shape": {
                            "kind": "poly",
                            "points": [
                                {"x": 0.0, "y": -12.5},
                                {"x": 12.5, "y": 0.0},
                                {"x": 0.0, "y": 12.5},
                                {"x": -12.5, "y": 0.0},
                            ],
                        },
                    }
                ),
            ],
        )
        self.systems.extend(
            [
                MinRenderSystem(),
            ]
        )
