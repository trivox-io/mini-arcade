"""
Example: entity/sprite_texture_basics
"""

from __future__ import annotations

from examples.catalog.entity._builder import build_entity_example

EXAMPLE_ID = "entity/sprite_texture_basics"
SCENE_ID = "sprite_texture_basics"
DISCOVER_PACKAGE = "examples.catalog.entity.sprite_texture_basics"


def build_example(**kwargs):
    return build_entity_example(
        example_id=EXAMPLE_ID,
        default_scene_id=SCENE_ID,
        default_discover_package=DISCOVER_PACKAGE,
        kwargs=kwargs,
        default_background_color=(14, 22, 24),
    )

