"""
Scene for entity/shape_primitives_gallery.
"""

from __future__ import annotations

from examples.catalog.entity._shared import (
    EntityExampleScene,
    EntityExampleWorld,
    ExampleSpinSystem,
    WorldClockSystem,
    build_render_system,
    entity_from_dict,
)
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.game_scene import GameSceneSystemsConfig
from mini_arcade_core.scenes.sim_scene import Drawable
from mini_arcade_core.scenes.systems.builtins import RenderOverlay

SCENE_ID = "shape_primitives_gallery"


class ShapeLabels(Drawable):
    """
    Draw small labels next to the gallery shapes.
    """

    def draw(self, backend, _ctx) -> None:
        labels = [
            (56, 82, "rect"),
            (240, 82, "circle"),
            (418, 82, "triangle"),
            (74, 286, "dashed line"),
            (292, 266, "poly"),
        ]
        for x, y, label in labels:
            backend.text.draw(
                x,
                y,
                label,
                color=(245, 245, 248),
                font_size=16,
            )


def _hud_lines(_ctx) -> list[str]:
    return [
        "Built-in entity rendering supports:",
        "- rect",
        "- circle",
        "- triangle",
        "- line",
        "- poly",
        "",
        "Use fill for solid shapes and stroke for",
        "outlines or dashed lines.",
        "",
        "ESC -> quit",
        "Next: entity/z_index_and_layer_intuition",
    ]


@register_scene(SCENE_ID)
class ShapePrimitivesGalleryScene(EntityExampleScene):
    """
    Gallery of the built-in shape kinds.
    """

    systems_config = GameSceneSystemsConfig(
        render_system_factory=lambda _runtime: build_render_system(
            title="entity/shape_primitives_gallery",
            lines_factory=_hud_lines,
            overlays=(
                RenderOverlay.from_drawable(ShapeLabels(), layer="ui", z=160),
            ),
        )
    )

    # pylint: disable=assignment-from-no-return
    def on_enter(self) -> None:
        """Create a gallery of primitive shapes with varied styling."""

        vw, vh = self.context.services.window.get_virtual_size()

        rect_entity = entity_from_dict(
            {
                "id": 1,
                "name": "Gallery Rect",
                "z_index": 2,
                "transform": {
                    "center": {"x": 46.0, "y": 118.0},
                    "size": {"width": 118.0, "height": 82.0},
                },
                "shape": {"kind": "rect", "corner_radius": 10.0},
                "style": {
                    "fill": [90, 208, 180, 255],
                    "stroke": {
                        "color": [220, 255, 246, 255],
                        "thickness": 2.0,
                    },
                },
            }
        )
        circle_entity = entity_from_dict(
            {
                "id": 2,
                "name": "Gallery Circle",
                "z_index": 2,
                "transform": {
                    "center": {"x": 228.0, "y": 110.0},
                    "size": {"width": 98.0, "height": 98.0},
                },
                "shape": {"kind": "circle", "radius": 49.0},
                "style": {
                    "fill": [255, 170, 84, 255],
                    "stroke": {
                        "color": [255, 233, 214, 255],
                        "thickness": 2.0,
                    },
                },
            }
        )
        triangle_entity = entity_from_dict(
            {
                "id": 3,
                "name": "Gallery Triangle",
                "z_index": 3,
                "transform": {
                    "center": {"x": 410.0, "y": 102.0},
                    "size": {"width": 120.0, "height": 108.0},
                    "rotation_deg": -16.0,
                },
                "shape": {"kind": "triangle"},
                "style": {
                    "stroke": {
                        "color": [140, 200, 255, 255],
                        "thickness": 2.0,
                    }
                },
            }
        )
        triangle_entity.spin_deg = 18.0

        dashed_line = entity_from_dict(
            {
                "id": 4,
                "name": "Gallery Line",
                "z_index": 1,
                "transform": {
                    "center": {"x": 72.0, "y": 326.0},
                    "size": {"width": 180.0, "height": 2.0},
                },
                "shape": {
                    "kind": "line",
                    "a": {"x": 0.0, "y": 0.0},
                    "b": {"x": 180.0, "y": 0.0},
                    "dash": {"length": 12.0, "gap": 8.0},
                },
                "style": {
                    "stroke": {
                        "color": [245, 245, 245, 255],
                        "thickness": 3.0,
                    }
                },
            }
        )
        poly_entity = entity_from_dict(
            {
                "id": 5,
                "name": "Gallery Poly",
                "z_index": 3,
                "transform": {
                    "center": {"x": 292.0, "y": 294.0},
                    "size": {"width": 118.0, "height": 118.0},
                    "rotation_deg": 4.0,
                },
                "shape": {
                    "kind": "poly",
                    "points": [
                        {"x": 0.0, "y": -1.0},
                        {"x": 0.86, "y": -0.18},
                        {"x": 0.55, "y": 0.92},
                        {"x": -0.55, "y": 0.92},
                        {"x": -0.86, "y": -0.18},
                    ],
                },
                "style": {
                    "fill": [214, 114, 255, 255],
                    "stroke": {
                        "color": [248, 230, 255, 255],
                        "thickness": 2.0,
                    },
                },
            }
        )
        poly_entity.spin_deg = -12.0

        self.world = EntityExampleWorld(
            viewport=(vw, vh),
            entities=[
                rect_entity,
                circle_entity,
                triangle_entity,
                dashed_line,
                poly_entity,
            ],
        )
        self.systems.extend([WorldClockSystem(), ExampleSpinSystem()])
