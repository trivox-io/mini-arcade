"""
Entry point for the mini_arcade_core package.
Provides access to core classes and a convenience function to run a game.

get_version method needs to be removed
"""

from __future__ import annotations

import traceback
from importlib.metadata import PackageNotFoundError, version
from typing import Any, Callable, Type, Union

from mini_arcade_core.backend import Backend
from mini_arcade_core.engine.engine_config import EngineConfig, SceneConfig
from mini_arcade_core.engine.game import Engine, EngineDependencies
from mini_arcade_core.scenes.registry import SceneRegistry
from mini_arcade_core.scenes.sim_scene import SimScene
from mini_arcade_core.utils import logger

SceneFactoryLike = Union[Type[SimScene], Callable[[Engine], SimScene]]


# TODO: Improve exception handliers by usingng and logging in run_game
def run_game(
    engine_config: EngineConfig | dict[str, Any] | None = None,
    backend: Backend | None = None,
    scene_config: SceneConfig | dict[str, Any] | None = None,
    gameplay_config: dict[str, Any] | None = None,
):
    """
    Convenience helper to bootstrap and run a game with a single scene.

    :param engine_config: Optional EngineConfig payload.
    :type engine_config: EngineConfig | dict[str, Any] | None

    :param backend: Optional Backend instance to use for the game.
    :type backend: Backend | None

    :param scene_config: Optional SceneConfig payload.
    :type scene_config: SceneConfig | dict[str, Any] | None

    :param gameplay_config: Optional gameplay settings payload.
    :type gameplay_config: dict[str, Any] | None

    :raises ValueError: If `backend` is missing.
    """
    try:
        if backend is None:
            raise ValueError(
                "A Backend instance must be provided to run the game."
            )

        raw_engine = engine_config or {}
        cfg = (
            raw_engine
            if isinstance(raw_engine, EngineConfig)
            else EngineConfig.from_dict(raw_engine)
        )

        if isinstance(scene_config, SceneConfig):
            scene_cfg = scene_config
        elif isinstance(scene_config, dict):
            scene_cfg = SceneConfig.from_dict(scene_config)
        else:
            scene_cfg = SceneConfig()

        scene_registry = SceneRegistry(_factories={}).discover(
            *scene_cfg.discover_packages
        )

        logger.debug(f"Discovered scenes: {scene_registry.listed_scene_ids}")
        game = Engine(
            cfg,
            EngineDependencies(
                backend=backend,
                scene_registry=scene_registry,
                gameplay_settings=gameplay_config,
            ),
        )
        initial_scene = scene_cfg.initial_scene or "main"
        game.run(initial_scene=initial_scene)
    # Justification: We want to log unexpected runtime failures before
    # propagating them to the caller.
    # pylint: disable=broad-exception-caught
    except Exception as e:
        logger.exception(f"Unhandled exception in game loop: {e}")
        logger.debug(traceback.format_exc())
        raise
    # pylint: enable=broad-exception-caught


PACKAGE_NAME = "mini-arcade-core"


def get_version() -> str:
    """
    Return the installed package version.

    This is a thin helper around importlib.metadata.version so games can do:

        from mini_arcade_core import get_version
        print(get_version())

    :return: The version string of the installed package.
    :rtype: str

    :raises PackageNotFoundError: If the package is not installed.
    """
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:  # if running from source / editable
        logger.warning(
            f"Package '{PACKAGE_NAME}' not found. Returning default version '0.0.0'."
        )
        return "0.0.0"


__all__ = [
    "Engine",
    "EngineDependencies",
    "EngineConfig",
    "SceneConfig",
    "run_game",
]

__version__ = get_version()
