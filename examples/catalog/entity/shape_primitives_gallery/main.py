"""
Example: entity/shape_primitives_gallery
"""

from __future__ import annotations

from examples.catalog.entity._builder import build_entity_example

EXAMPLE_ID = "entity/shape_primitives_gallery"
SCENE_ID = "shape_primitives_gallery"
DISCOVER_PACKAGE = "examples.catalog.entity.shape_primitives_gallery"


def build_example(**kwargs):
    """Build the example spec for the shape-primitives tutorial scene."""

    return build_entity_example(
        example_id=EXAMPLE_ID,
        default_scene_id=SCENE_ID,
        default_discover_package=DISCOVER_PACKAGE,
        kwargs=kwargs,
        default_background_color=(18, 17, 28),
    )
