"""
Scene for entity/sprite_texture_basics.
"""

from __future__ import annotations

# isort owns import ordering; pylint misclassifies local packages as third-party.
# pylint: disable=wrong-import-order
from examples.catalog.entity._shared import (
    EntityExampleScene,
    EntityExampleWorld,
    ExampleSpinSystem,
    WorldClockSystem,
    build_render_system,
    entity_from_dict,
)
from examples.catalog.entity._textures import (
    checker_texture,
    diamond_texture,
    stripe_texture,
)
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.game_scene import GameSceneSystemsConfig
from mini_arcade_core.scenes.sim_scene import Drawable
from mini_arcade_core.scenes.systems.builtins import RenderOverlay

SCENE_ID = "sprite_texture_basics"


class SpriteLabels(Drawable):
    """
    Draw labels for the sprite example entities.
    """

    def draw(self, backend, _ctx) -> None:
        labels = [
            (54, 82, "checker texture"),
            (248, 82, "scaled stripes"),
            (86, 282, "rotating diamond sprite"),
            (296, 302, "shape fallback"),
        ]
        for x, y, label in labels:
            backend.text.draw(
                x,
                y,
                label,
                color=(240, 244, 244),
                font_size=16,
            )


def _hud_lines(_ctx) -> list[str]:
    return [
        "If sprite.texture exists, rendering uses that",
        "texture instead of the entity shape.",
        "",
        "The same texture can be scaled, stretched, or",
        "rotated by the entity transform.",
        "",
        "The white block on the right has no sprite, so",
        "it falls back to shape + style rendering.",
        "",
        "ESC -> quit",
        "Next: entity/animation_frames_basics",
    ]


@register_scene(SCENE_ID)
class SpriteTextureBasicsScene(EntityExampleScene):
    """
    Demonstrates sprite textures and transform-driven scaling.
    """

    systems_config = GameSceneSystemsConfig(
        render_system_factory=lambda _runtime: build_render_system(
            title="entity/sprite_texture_basics",
            lines_factory=_hud_lines,
            overlays=(
                RenderOverlay.from_drawable(SpriteLabels(), layer="ui", z=160),
            ),
        )
    )

    # pylint: disable=assignment-from-no-return
    def on_enter(self) -> None:
        """Create sample entities that render procedurally generated textures."""

        vw, vh = self.context.services.window.get_virtual_size()
        backend_render = self.context.services.render.backend.render

        tex_checker = self.remember_texture(
            checker_texture(
                backend_render,
                width=18,
                height=18,
                color_a=(72, 212, 188, 255),
                color_b=(20, 84, 92, 255),
                cell=3,
            )
        )
        tex_stripes = self.remember_texture(
            stripe_texture(
                backend_render,
                width=18,
                height=18,
                base=(54, 70, 150, 255),
                stripe=(214, 240, 255, 255),
                stripe_width=3,
            )
        )
        tex_diamond = self.remember_texture(
            diamond_texture(
                backend_render,
                size=20,
                fill=(255, 172, 82, 255),
                outline=(255, 245, 214, 255),
            )
        )

        checker_entity = entity_from_dict(
            {
                "id": 1,
                "name": "Checker Sprite",
                "transform": {
                    "center": {"x": 52.0, "y": 118.0},
                    "size": {"width": 112.0, "height": 112.0},
                },
                "shape": {"kind": "rect"},
                "sprite": {"texture": tex_checker},
            }
        )
        stripe_entity = entity_from_dict(
            {
                "id": 2,
                "name": "Stripe Sprite",
                "transform": {
                    "center": {"x": 240.0, "y": 118.0},
                    "size": {"width": 170.0, "height": 64.0},
                },
                "shape": {"kind": "rect"},
                "sprite": {"texture": tex_stripes},
            }
        )
        diamond_entity = entity_from_dict(
            {
                "id": 3,
                "name": "Diamond Sprite",
                "transform": {
                    "center": {"x": 104.0, "y": 318.0},
                    "size": {"width": 128.0, "height": 128.0},
                },
                "shape": {"kind": "rect"},
                "sprite": {"texture": tex_diamond},
            }
        )
        diamond_entity.spin_deg = 64.0

        fallback_entity = entity_from_dict(
            {
                "id": 4,
                "name": "Fallback Block",
                "transform": {
                    "center": {"x": 300.0, "y": 320.0},
                    "size": {"width": 112.0, "height": 112.0},
                },
                "shape": {"kind": "rect", "corner_radius": 12.0},
                "style": {
                    "fill": [235, 235, 238, 255],
                    "stroke": {
                        "color": [120, 120, 124, 255],
                        "thickness": 2.0,
                    },
                },
            }
        )

        self.world = EntityExampleWorld(
            viewport=(vw, vh),
            entities=[
                checker_entity,
                stripe_entity,
                diamond_entity,
                fallback_entity,
            ],
        )
        self.systems.extend([WorldClockSystem(), ExampleSpinSystem()])
