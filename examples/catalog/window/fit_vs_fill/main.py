"""
Example: window/fit_vs_fill
"""

from __future__ import annotations

from examples.catalog.window._builder import build_window_example

EXAMPLE_ID = "window/fit_vs_fill"
DEFAULT_SCENE_ID = "fit_vs_fill"
DEFAULT_DISCOVER_PACKAGE = "examples.catalog.window.fit_vs_fill"


def build_example(**kwargs):
    """
    Build tutorial spec for fit vs fill viewport behavior.
    """
    return build_window_example(
        example_id=EXAMPLE_ID,
        default_scene_id=DEFAULT_SCENE_ID,
        default_discover_package=DEFAULT_DISCOVER_PACKAGE,
        kwargs=kwargs,
        default_background_color=(8, 10, 16),
    )

