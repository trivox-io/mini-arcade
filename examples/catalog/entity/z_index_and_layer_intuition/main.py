"""
Example: entity/z_index_and_layer_intuition
"""

from __future__ import annotations

from examples.catalog.entity._builder import build_entity_example

EXAMPLE_ID = "entity/z_index_and_layer_intuition"
SCENE_ID = "z_index_and_layer_intuition"
DISCOVER_PACKAGE = "examples.catalog.entity.z_index_and_layer_intuition"


def build_example(**kwargs):
    return build_entity_example(
        example_id=EXAMPLE_ID,
        default_scene_id=SCENE_ID,
        default_discover_package=DISCOVER_PACKAGE,
        kwargs=kwargs,
        default_background_color=(20, 16, 22),
    )

