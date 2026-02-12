"""
Example: 002_hello_overlay
"""

from __future__ import annotations

# pylint: disable=import-error
from examples._shared.defaults import make_default_backend_factory
from examples._shared.spec import ExampleSpec


def build_example(**_kwargs) -> ExampleSpec:
    discover = [
        "examples.scenes.002_hello_overlay",
        "mini_arcade_core.scenes",
    ]

    return ExampleSpec(
        discover_packages=discover,
        initial_scene="min",
        fps=60,
        backend_factory=make_default_backend_factory(
            title="Example: 002_hello_overlay"
        ),
    )
