"""
Example: 003_simple_shape
"""

from __future__ import annotations

# pylint: disable=import-error
from examples._shared.defaults import make_default_backend_factory
from examples._shared.spec import ExampleSpec


def build_example(**_kwargs) -> ExampleSpec:
    """
    Build the example spec.

    :return: the example spec
    :rtype: ExampleSpec
    """
    discover = [
        "examples.scenes.003_simple_shape",
        "mini_arcade_core.scenes",
    ]

    return ExampleSpec(
        discover_packages=discover,
        initial_scene="min",
        fps=60,
        backend_factory=make_default_backend_factory(
            title="Example: 003_simple_shape"
        ),
    )
