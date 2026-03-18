"""
Example: systems/phases_and_order

Demonstrates how SystemPhase and per-system order control execution
sequence inside a SystemPipeline.
"""

from __future__ import annotations

# isort owns import ordering; pylint misclassifies local packages as third-party.
# pylint: disable=wrong-import-order
from typing import Any

from examples._shared.defaults import make_backend_factory
from examples._shared.spec import ExampleSpec
from mini_arcade.modules.settings import Settings
from mini_arcade_core import EngineConfig
from mini_arcade_core.engine.engine_config import PostFXConfig

EXAMPLE_ID = "systems/phases_and_order"
DEFAULT_SCENE_ID = "phases_and_order"
DEFAULT_DISCOVER_PACKAGES = [
    "examples.catalog.systems.phases_and_order",
    "mini_arcade_core.scenes",
]


def _arg_or_default(kwargs: dict[str, Any], key: str, default: Any) -> Any:
    value = kwargs.get(key, default)
    return default if value is None else value


def build_example(**kwargs) -> ExampleSpec:
    """Build tutorial spec for phases and order example."""
    settings = Settings.for_example(EXAMPLE_ID, required=False)
    engine_defaults = settings.engine_config_defaults()
    scene_defaults = settings.scene_defaults()
    backend_defaults = settings.backend_defaults(resolve_paths=True)

    backend = (
        str(
            _arg_or_default(
                kwargs,
                "backend",
                backend_defaults.get("provider", "pygame"),
            )
        )
        .lower()
        .strip()
    )

    fps = int(_arg_or_default(kwargs, "fps", engine_defaults.get("fps", 60)))

    discover = scene_defaults.get("discover_packages", [])
    if not isinstance(discover, list) or not discover:
        discover = list(DEFAULT_DISCOVER_PACKAGES)
    initial_scene = str(scene_defaults.get("initial_scene", DEFAULT_SCENE_ID))

    def _engine_config_factory(_backend_impl):
        return EngineConfig(
            fps=fps,
            virtual_resolution=(800, 600),
            postfx=PostFXConfig(enabled=False),
        )

    return ExampleSpec(
        discover_packages=discover,
        initial_scene=initial_scene,
        fps=fps,
        backend_factory=make_backend_factory(
            title=f"{EXAMPLE_ID} ({backend})",
            backend=backend,
            width=960,
            height=540,
            background_color=(16, 18, 28),
        ),
        engine_config_factory=_engine_config_factory,
    )
