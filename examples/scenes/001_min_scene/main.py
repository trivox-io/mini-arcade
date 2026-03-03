"""
Example: 001_min_scene
"""

from __future__ import annotations

# pylint: disable=import-error
from examples._shared.defaults import make_default_backend_factory
from examples._shared.spec import ExampleSpec


def build_example(**_kwargs) -> ExampleSpec:
    """
    Build and return the ExampleSpec for this example.

    :return: The ExampleSpec instance for this example.
    :rtype: ExampleSpec
    """
    discover = [
        "examples.scenes.001_min_scene",
        "mini_arcade_core.scenes",
    ]

    return ExampleSpec(
        discover_packages=discover,
        initial_scene="min",
        fps=60,
        backend_factory=make_default_backend_factory(
            title="Example: 001_min_scene"
        ),
    )
