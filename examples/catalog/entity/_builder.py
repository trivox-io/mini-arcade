"""
Shared builder helpers for entity tutorials.
"""

from __future__ import annotations

from typing import Any

from examples.catalog.window._builder import build_window_example
from examples._shared.spec import ExampleSpec


def build_entity_example(
    *,
    example_id: str,
    default_scene_id: str,
    default_discover_package: str,
    kwargs: dict[str, Any],
    default_background_color: tuple[int, int, int],
) -> ExampleSpec:
    """
    Build an entity tutorial ExampleSpec using the shared example conventions.
    """
    return build_window_example(
        example_id=example_id,
        default_scene_id=default_scene_id,
        default_discover_package=default_discover_package,
        kwargs=kwargs,
        default_background_color=default_background_color,
    )

