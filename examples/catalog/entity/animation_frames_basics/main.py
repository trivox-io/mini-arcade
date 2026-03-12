"""
Example: entity/animation_frames_basics
"""

from __future__ import annotations

from examples.catalog.entity._builder import build_entity_example

EXAMPLE_ID = "entity/animation_frames_basics"
SCENE_ID = "animation_frames_basics"
DISCOVER_PACKAGE = "examples.catalog.entity.animation_frames_basics"


def build_example(**kwargs):
    """Build the example spec for the animation-frames tutorial scene."""

    return build_entity_example(
        example_id=EXAMPLE_ID,
        default_scene_id=SCENE_ID,
        default_discover_package=DISCOVER_PACKAGE,
        kwargs=kwargs,
        default_background_color=(18, 18, 20),
    )
