"""
Example: window/resize_reflow
"""

from __future__ import annotations

from examples.catalog.window._builder import build_window_example

EXAMPLE_ID = "window/resize_reflow"
DEFAULT_SCENE_ID = "resize_reflow"
DEFAULT_DISCOVER_PACKAGE = "examples.catalog.window.resize_reflow"


def build_example(**kwargs):
    """
    Build tutorial spec for resize reflow behavior.
    """
    return build_window_example(
        example_id=EXAMPLE_ID,
        default_scene_id=DEFAULT_SCENE_ID,
        default_discover_package=DEFAULT_DISCOVER_PACKAGE,
        kwargs=kwargs,
        default_background_color=(9, 12, 20),
    )

