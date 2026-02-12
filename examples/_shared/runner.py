"""
Example runner.
"""

from __future__ import annotations

import importlib
from typing import Any

from mini_arcade.utils.logging import logger  # type: ignore[import-not-found]
from mini_arcade_core import (  # type: ignore[import-not-found]
    GameConfig,
    SceneRegistry,
    run_game,
)

from .spec import ExampleSpec


class ExampleLoadError(RuntimeError):
    """
    Raised when there is an error loading an example module or its spec.
    """


def _import_example_main(example_id: str) -> Any:
    """
    Import examples.scenes.<example_id>.main

    Example id:
      - "001_min_scene"
    """
    mod_name = f"examples.scenes.{example_id}.main"
    try:
        return importlib.import_module(mod_name)
    except Exception as e:  # noqa: BLE001
        raise ExampleLoadError(
            f"Failed to import example module: {mod_name}"
        ) from e


def load_example_spec(example_id: str, **kwargs) -> ExampleSpec:
    """
    Load ExampleSpec by calling build_example(**kwargs) in the example main module.

    :param example_id: Example id to load (e.g. "001_min_scene")
    :type example_id: str
    :param kwargs: Keyword arguments to pass to build_example()
    :type kwargs: dict
    :return: Loaded ExampleSpec instance
    :rtype: ExampleSpec
    :raises ExampleLoadError: If there is an error loading the example or its spec
    """
    mod = _import_example_main(example_id)
    build = getattr(mod, "build_example", None)
    if build is None or not callable(build):
        raise ExampleLoadError(
            f"Example '{example_id}' must define build_example(**kwargs) -> ExampleSpec"
        )
    spec = build(**kwargs)
    if not isinstance(spec, ExampleSpec):
        raise ExampleLoadError(
            f"Example '{example_id}' build_example() must return ExampleSpec"
        )
    return spec


def run_example(example_id: str, **kwargs) -> int:
    """
    Run an example by id.

    kwargs can include things like:
      - backend="native"|"pygame"
      - window_size=(w,h)
      - title="..."
      - enable_audio=True
      - etc (each example can accept what it wants)
    """
    spec = load_example_spec(example_id, **kwargs)

    scene_registry = SceneRegistry(_factories={}).discover(
        *spec.discover_packages
    )

    backend = spec.backend_factory()

    if spec.game_config_factory:
        game_config = spec.game_config_factory(backend, scene_registry)
    else:
        game_config = GameConfig(
            initial_scene=spec.initial_scene,
            fps=spec.fps,
            backend=backend,
        )

    logger.info(
        f"Starting example: {example_id} (scene={spec.initial_scene}, fps={spec.fps})"
    )
    run_game(game_config=game_config, scene_registry=scene_registry)
    return 0
