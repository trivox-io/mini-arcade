"""
Example: entity/base_entity_from_dict
"""

from __future__ import annotations

from examples.catalog.entity._builder import build_entity_example

EXAMPLE_ID = "entity/base_entity_from_dict"
SCENE_ID = "base_entity_from_dict"
DISCOVER_PACKAGE = "examples.catalog.entity.base_entity_from_dict"


def build_example(**kwargs):
    """Build the example spec for the entity-from-dict tutorial scene."""

    return build_entity_example(
        example_id=EXAMPLE_ID,
        default_scene_id=SCENE_ID,
        default_discover_package=DISCOVER_PACKAGE,
        kwargs=kwargs,
        default_background_color=(15, 19, 31),
    )
