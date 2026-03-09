"""
Example: window/virtual_resolution_basics
"""

from __future__ import annotations

from examples.catalog.window._builder import build_window_example

EXAMPLE_ID = "window/virtual_resolution_basics"
DEFAULT_SCENE_ID = "virtual_resolution_basics"
DEFAULT_DISCOVER_PACKAGE = "examples.catalog.window.virtual_resolution_basics"


def build_example(**kwargs):
    """
    Build tutorial spec for virtual resolution basics.
    """
    return build_window_example(
        example_id=EXAMPLE_ID,
        default_scene_id=DEFAULT_SCENE_ID,
        default_discover_package=DEFAULT_DISCOVER_PACKAGE,
        kwargs=kwargs,
        default_background_color=(10, 12, 18),
    )

