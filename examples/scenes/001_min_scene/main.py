"""
Example: 001_min_scene
"""

from __future__ import annotations

# Justification: False positive for import-error; this is the intended way to run examples.
# pylint: disable=import-error
from examples._shared.spec import ExampleSpec

# pick backend here for now; keep it simple.
# Later you can read CLI passthrough args and select pygame/native.


def build_example(**_kwargs) -> ExampleSpec:
    """
    Build the ExampleSpec for this example.
    The shared runner will:
        - discover scenes from `discover_packages`
        - build backend via `backend_factory`
        - build GameConfig and call run_game(...)
    You can also use kwargs to customize the spec based on CLI passthrough args.

    :param _kwargs: Keyword arguments to customize the example spec (currently unused)
    :type _kwargs: dict
    :return: ExampleSpec instance for this example
    :rtype: ExampleSpec
    :raises ExampleLoadError: If there is an error building the example spec
    """
    # IMPORTANT: your example scene package should contain the registered scenes
    # and your scene id must match `initial_scene`.
    discover = [
        "examples.scenes.001_min_scene",
        "mini_arcade_core.scenes",
    ]

    def backend_factory():
        # TODO: choose backend properly later
        from mini_arcade_pygame_backend import (  # type: ignore[import-not-found] pylint: disable=import-outside-toplevel
            PygameBackend,
            PygameBackendSettings,
        )

        settings = PygameBackendSettings.from_dict(
            {
                "window": {
                    "width": 800,
                    "height": 600,
                    "title": "Example: 001_min_scene",
                    "resizable": True,
                },
                "renderer": {"background_color": (20, 20, 20)},
            }
        )
        return PygameBackend(settings=settings)

    return ExampleSpec(
        discover_packages=discover,
        initial_scene="min",  # must match your @register_scene("min")
        fps=60,
        backend_factory=backend_factory,
    )
