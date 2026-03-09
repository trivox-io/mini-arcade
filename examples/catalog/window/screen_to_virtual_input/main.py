"""
Example: window/screen_to_virtual_input
"""

from __future__ import annotations

from examples.catalog.window._builder import build_window_example

EXAMPLE_ID = "window/screen_to_virtual_input"
DEFAULT_SCENE_ID = "screen_to_virtual_input"
DEFAULT_DISCOVER_PACKAGE = "examples.catalog.window.screen_to_virtual_input"


def build_example(**kwargs):
    """
    Build tutorial spec for screen-to-virtual input mapping.
    """
    return build_window_example(
        example_id=EXAMPLE_ID,
        default_scene_id=DEFAULT_SCENE_ID,
        default_discover_package=DEFAULT_DISCOVER_PACKAGE,
        kwargs=kwargs,
        default_background_color=(8, 10, 16),
    )

