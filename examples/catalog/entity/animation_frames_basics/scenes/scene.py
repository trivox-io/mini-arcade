"""
Scene for entity/animation_frames_basics.
"""

from __future__ import annotations

from examples.catalog.entity._shared import (
    EntityExampleScene,
    EntityExampleWorld,
    ExampleAnimationSystem,
    WorldClockSystem,
    build_render_system,
    entity_from_dict,
)
from examples.catalog.entity._textures import orb_frame_texture
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.game_scene import GameSceneSystemsConfig
from mini_arcade_core.scenes.sim_scene import Drawable
from mini_arcade_core.scenes.systems.builtins import RenderOverlay

SCENE_ID = "animation_frames_basics"
ANIM_FAST_ID = 2


class AnimationLabels(Drawable):
    """
    Draw labels for the animated entities.
    """

    def draw(self, backend, _ctx) -> None:
        labels = [
            (78, 88, "loop fps=6"),
            (264, 88, "loop fps=12"),
            (114, 306, "static frame"),
        ]
        for x, y, text in labels:
            backend.text.draw(
                x,
                y,
                text,
                color=(245, 245, 245),
                font_size=16,
            )


def _hud_lines(ctx) -> list[str]:
    fast = ctx.world.get_entity_by_id(ANIM_FAST_ID)
    anim_index = "n/a"
    if fast is not None and fast.anim is not None:
        anim_index = str(fast.anim.anim.index)
    return [
        "An entity with anim.frames renders the current",
        "animation frame each tick.",
        "",
        "You still need a system that calls anim.step(dt).",
        "This example uses one loop at fps=6 and one at",
        "fps=12 so the timing difference is visible.",
        "",
        f"fast animation frame index: {anim_index}",
        "ESC -> quit",
        "Next: systems/input_frame_visualizer",
    ]


@register_scene(SCENE_ID)
class AnimationFramesBasicsScene(EntityExampleScene):
    """
    Demonstrates frame-based animation on entities.
    """

    systems_config = GameSceneSystemsConfig(
        render_system_factory=lambda _runtime: build_render_system(
            title="entity/animation_frames_basics",
            lines_factory=_hud_lines,
            overlays=(
                RenderOverlay.from_drawable(
                    AnimationLabels(), layer="ui", z=160
                ),
            ),
        )
    )

    # pylint: disable=assignment-from-no-return
    def on_enter(self) -> None:
        """Create animated sample entities and register the example world."""

        vw, vh = self.context.services.window.get_virtual_size()
        backend_render = self.context.services.render.backend.render
        frames = [
            self.remember_texture(
                orb_frame_texture(
                    backend_render,
                    size=24,
                    inner=inner,
                    outer=outer,
                )
            )
            for inner, outer in (
                ((255, 246, 214, 255), (255, 168, 74, 255)),
                ((235, 250, 255, 255), (96, 194, 255, 255)),
                ((247, 231, 255, 255), (208, 118, 255, 255)),
                ((224, 255, 228, 255), (112, 228, 138, 255)),
            )
        ]

        slow_anim = entity_from_dict(
            {
                "id": 1,
                "name": "Slow Pulse",
                "transform": {
                    "center": {"x": 72.0, "y": 124.0},
                    "size": {"width": 120.0, "height": 120.0},
                },
                "shape": {"kind": "rect"},
                "anim": {"frames": frames, "fps": 6.0, "loop": True},
            }
        )
        fast_anim = entity_from_dict(
            {
                "id": ANIM_FAST_ID,
                "name": "Fast Pulse",
                "transform": {
                    "center": {"x": 248.0, "y": 124.0},
                    "size": {"width": 120.0, "height": 120.0},
                },
                "shape": {"kind": "rect"},
                "anim": {"frames": frames, "fps": 12.0, "loop": True},
            }
        )
        static_frame = entity_from_dict(
            {
                "id": 3,
                "name": "Static Preview",
                "transform": {
                    "center": {"x": 118.0, "y": 338.0},
                    "size": {"width": 180.0, "height": 84.0},
                },
                "shape": {"kind": "rect"},
                "sprite": {"texture": frames[0]},
            }
        )

        self.world = EntityExampleWorld(
            viewport=(vw, vh),
            entities=[slow_anim, fast_anim, static_frame],
        )
        self.systems.extend([WorldClockSystem(), ExampleAnimationSystem()])
