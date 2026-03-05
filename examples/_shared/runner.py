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


def _normalized_example_id(example_id: str) -> str:
    """
    Normalize slash-separated example id.
    """
    normalized = str(example_id).replace("\\", "/").strip("/")
    if not normalized:
        raise ExampleLoadError("Example id must be non-empty")
    return normalized


def _import_example_main(example_id: str) -> Any:
    """
    Import the example module by id.

    Grouped id examples:
        - "config/engine_config_basics"
        - "render/world_pass"
    """
    normalized = _normalized_example_id(example_id)
    dotted = normalized.replace("/", ".")

    # New grouped catalog path first, then legacy scenes path fallback.
    candidates = [
        f"examples.catalog.{dotted}.main",
        f"examples.scenes.{dotted}.main",
    ]
    last_error: Exception | None = None
    for mod_name in candidates:
        try:
            return importlib.import_module(mod_name)
        except Exception as exc:  # noqa: BLE001
            last_error = exc

    raise ExampleLoadError(
        f"Failed to import example module for id '{normalized}'. "
        f"Tried: {', '.join(candidates)}"
    ) from last_error


def load_example_spec(example_id: str, **kwargs) -> ExampleSpec:
    """
    Load ExampleSpec by calling build_example(**kwargs) in the example main module.

    :param example_id: Example id to load (e.g. "config/engine_config_basics")
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

    :param example_id: Example id to run (e.g. "config/engine_config_basics")
    :type example_id: str
    :param kwargs: Keyword arguments to pass to the example spec builder
    :type kwargs: dict
    :return: Exit code (0 for success)
    :rtype: int
    :raises ExampleLoadError: If there is an error loading the example or its spec
    """
    normalized = _normalized_example_id(example_id)
    spec = load_example_spec(normalized, **kwargs)

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
        f"Starting example: {normalized} (scene={spec.initial_scene}, fps={spec.fps})"
    )
    run_game(game_config=game_config, scene_registry=scene_registry)
    return 0
