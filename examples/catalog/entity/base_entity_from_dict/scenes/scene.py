"""
Scene for entity/base_entity_from_dict.
"""

from __future__ import annotations

from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.game_scene import GameSceneSystemsConfig

from examples.catalog.entity._shared import (
    EntityExampleScene,
    EntityExampleWorld,
    ExampleMotionSystem,
    ExampleSpinSystem,
    WorldClockSystem,
    build_render_system,
    entity_from_dict,
)

SCENE_ID = "base_entity_from_dict"
COURIER_ID = 1


def _hud_lines(ctx) -> list[str]:
    courier = ctx.world.get_entity_by_id(COURIER_ID)
    courier_pos = "n/a"
    courier_vel = "n/a"
    if courier is not None and courier.kinematic is not None:
        courier_pos = (
            f"({courier.transform.center.x:.0f},"
            f" {courier.transform.center.y:.0f})"
        )
        courier_vel = (
            f"({courier.kinematic.velocity.x:.0f},"
            f" {courier.kinematic.velocity.y:.0f})"
        )
    return [
        "Build one entity payload as plain data, then",
        "hand it to BaseEntity.from_dict(...).",
        "",
        "Mapped fields:",
        "- transform + shape",
        "- style + z_index",
        "- kinematic + collider",
        "",
        f"courier pos: {courier_pos}",
        f"courier vel: {courier_vel}",
        "ESC -> quit",
        "Next: entity/shape_primitives_gallery",
    ]


@register_scene(SCENE_ID)
class BaseEntityFromDictScene(EntityExampleScene):
    """
    Demonstrates the ``BaseEntity.from_dict(...)`` contract.
    """

    systems_config = GameSceneSystemsConfig(
        render_system_factory=lambda _runtime: build_render_system(
            title="entity/base_entity_from_dict",
            lines_factory=_hud_lines,
        )
    )

    # pylint: disable=assignment-from-no-return
    def on_enter(self) -> None:
        """Create entities from literal payload dictionaries for inspection."""

        vw, vh = self.context.services.window.get_virtual_size()

        courier = entity_from_dict(
            {
                "id": COURIER_ID,
                "name": "Courier Block",
                "z_index": 5,
                "transform": {
                    "center": {"x": 56.0, "y": 236.0},
                    "size": {"width": 96.0, "height": 56.0},
                },
                "shape": {"kind": "rect", "corner_radius": 8.0},
                "style": {
                    "fill": [82, 193, 255, 255],
                    "stroke": {
                        "color": [220, 244, 255, 255],
                        "thickness": 2.0,
                    },
                },
                "collider": {"kind": "rect"},
                "kinematic": {
                    "velocity": {"vx": 150.0, "vy": 0.0},
                    "acceleration": {"ax": 0.0, "ay": 0.0},
                    "max_speed": 150.0,
                },
            }
        )
        courier.example_motion_enabled = True

        beacon = entity_from_dict(
            {
                "id": 2,
                "name": "Outline Beacon",
                "z_index": 3,
                "transform": {
                    "center": {"x": 284.0, "y": 112.0},
                    "size": {"width": 124.0, "height": 124.0},
                    "rotation_deg": 12.0,
                },
                "shape": {"kind": "triangle"},
                "style": {
                    "stroke": {
                        "color": [255, 210, 100, 255],
                        "thickness": 2.0,
                    }
                },
            }
        )
        beacon.spin_deg = 28.0

        anchor = entity_from_dict(
            {
                "id": 3,
                "name": "Anchor Orb",
                "z_index": 2,
                "transform": {
                    "center": {"x": 252.0, "y": 328.0},
                    "size": {"width": 96.0, "height": 96.0},
                },
                "shape": {"kind": "circle", "radius": 48.0},
                "style": {
                    "fill": [255, 140, 110, 255],
                    "stroke": {
                        "color": [255, 232, 224, 255],
                        "thickness": 2.0,
                    },
                },
                "collider": {"kind": "circle", "radius": 48.0},
            }
        )

        runway = entity_from_dict(
            {
                "id": 4,
                "name": "Guide Line",
                "z_index": 1,
                "transform": {
                    "center": {"x": 48.0, "y": 264.0},
                    "size": {"width": 360.0, "height": 2.0},
                },
                "shape": {
                    "kind": "line",
                    "a": {"x": 0.0, "y": 0.0},
                    "b": {"x": 360.0, "y": 0.0},
                    "dash": {"length": 18.0, "gap": 10.0},
                },
                "style": {
                    "stroke": {
                        "color": [90, 96, 116, 255],
                        "thickness": 2.0,
                    }
                },
            }
        )

        self.world = EntityExampleWorld(
            viewport=(vw, vh),
            entities=[runway, beacon, anchor, courier],
        )
        self.systems.extend(
            [
                WorldClockSystem(),
                ExampleMotionSystem(),
                ExampleSpinSystem(),
            ]
        )
