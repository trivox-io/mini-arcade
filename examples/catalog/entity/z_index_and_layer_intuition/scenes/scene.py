"""
Scene for entity/z_index_and_layer_intuition.
"""

from __future__ import annotations

from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.game_scene import GameSceneSystemsConfig
from mini_arcade_core.scenes.sim_scene import Drawable
from mini_arcade_core.scenes.systems.builtins import RenderOverlay

from examples.catalog.entity._shared import (
    EntityExampleScene,
    EntityExampleWorld,
    ExampleSpinSystem,
    WorldClockSystem,
    build_render_system,
    entity_from_dict,
)

SCENE_ID = "z_index_and_layer_intuition"


class LayerLabels(Drawable):
    """
    Draw explanatory labels over the layered entities.
    """

    def draw(self, backend, _ctx) -> None:
        labels = [
            (72, 132, "world z=1"),
            (116, 188, "world z=4"),
            (170, 244, "world z=8"),
            (420, 78, "layer=ui"),
        ]
        for x, y, text in labels:
            backend.text.draw(
                x,
                y,
                text,
                color=(248, 248, 248),
                font_size=16,
            )


def _hud_lines(_ctx) -> list[str]:
    return [
        "z_index sorts entities inside the same layer.",
        "render_layer moves an entity to another pass.",
        "",
        "Here the stacked cards are all world-layer.",
        "The gold badge is still an entity, but it lives",
        "in the ui layer so it stays above the stack.",
        "",
        "ESC -> quit",
        "Next: entity/sprite_texture_basics",
    ]


@register_scene(SCENE_ID)
class ZIndexAndLayerIntuitionScene(EntityExampleScene):
    """
    Makes z-index and render-layer ordering visible.
    """

    systems_config = GameSceneSystemsConfig(
        render_system_factory=lambda _runtime: build_render_system(
            title="entity/z_index_and_layer_intuition",
            lines_factory=_hud_lines,
            overlays=(
                RenderOverlay.from_drawable(LayerLabels(), layer="ui", z=160),
            ),
        )
    )

    def on_enter(self) -> None:
        vw, vh = self.context.services.window.get_virtual_size()

        back_card = entity_from_dict(
            {
                "id": 1,
                "name": "Back Card",
                "z_index": 1,
                "transform": {
                    "center": {"x": 54.0, "y": 156.0},
                    "size": {"width": 206.0, "height": 138.0},
                },
                "shape": {"kind": "rect", "corner_radius": 16.0},
                "style": {
                    "fill": [95, 112, 208, 255],
                    "stroke": {
                        "color": [219, 226, 255, 255],
                        "thickness": 2.0,
                    },
                },
            }
        )
        mid_card = entity_from_dict(
            {
                "id": 2,
                "name": "Mid Card",
                "z_index": 4,
                "transform": {
                    "center": {"x": 108.0, "y": 208.0},
                    "size": {"width": 206.0, "height": 138.0},
                },
                "shape": {"kind": "rect", "corner_radius": 16.0},
                "style": {
                    "fill": [94, 194, 154, 255],
                    "stroke": {
                        "color": [224, 254, 244, 255],
                        "thickness": 2.0,
                    },
                },
            }
        )
        top_card = entity_from_dict(
            {
                "id": 3,
                "name": "Top Card",
                "z_index": 8,
                "transform": {
                    "center": {"x": 164.0, "y": 260.0},
                    "size": {"width": 206.0, "height": 138.0},
                },
                "shape": {"kind": "rect", "corner_radius": 16.0},
                "style": {
                    "fill": [240, 118, 138, 255],
                    "stroke": {
                        "color": [255, 226, 233, 255],
                        "thickness": 2.0,
                    },
                },
            }
        )

        badge = entity_from_dict(
            {
                "id": 4,
                "name": "Ui Badge",
                "z_index": 0,
                "transform": {
                    "center": {"x": 404.0, "y": 60.0},
                    "size": {"width": 174.0, "height": 72.0},
                },
                "shape": {"kind": "rect", "corner_radius": 18.0},
                "style": {
                    "fill": [255, 205, 74, 255],
                    "stroke": {
                        "color": [255, 246, 204, 255],
                        "thickness": 2.0,
                    },
                },
            }
        )
        badge.render_layer = "ui"

        spinner = entity_from_dict(
            {
                "id": 5,
                "name": "Spinner",
                "z_index": 6,
                "transform": {
                    "center": {"x": 272.0, "y": 120.0},
                    "size": {"width": 72.0, "height": 72.0},
                },
                "shape": {
                    "kind": "poly",
                    "points": [
                        {"x": 0.0, "y": -1.0},
                        {"x": 1.0, "y": 0.0},
                        {"x": 0.0, "y": 1.0},
                        {"x": -1.0, "y": 0.0},
                    ],
                },
                "style": {
                    "stroke": {
                        "color": [255, 255, 255, 255],
                        "thickness": 2.0,
                    }
                },
            }
        )
        spinner.spin_deg = 38.0

        self.world = EntityExampleWorld(
            viewport=(vw, vh),
            entities=[back_card, mid_card, spinner, top_card, badge],
        )
        self.systems.extend([WorldClockSystem(), ExampleSpinSystem()])
