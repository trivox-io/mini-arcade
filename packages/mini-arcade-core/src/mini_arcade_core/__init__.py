"""
Entry point for the mini_arcade_core package.
Provides access to core classes and a convenience function to run a game.

get_version method needs to be removed
"""

from __future__ import annotations

import traceback
from importlib.metadata import PackageNotFoundError, version
from typing import Callable, Type, Union

from mini_arcade_core.engine.game import Game
from mini_arcade_core.engine.game_config import GameConfig
from mini_arcade_core.scenes.registry import SceneRegistry
from mini_arcade_core.scenes.sim_scene import SimScene
from mini_arcade_core.utils import logger

SceneFactoryLike = Union[Type[SimScene], Callable[[Game], SimScene]]


# TODO: Improve exception handliers by usingng and logging in run_game
def run_game(
    game_config: GameConfig | None = None,
    scene_registry: SceneRegistry | None = None,
):
    """
    Convenience helper to bootstrap and run a game with a single scene.

    :param game_config: Optional GameConfig to customize game settings.
    :type game_config: GameConfig | None

    :param scene_registry: Optional SceneRegistry for scene management.
    :type scene_registry: SceneRegistry | None

    :raises ValueError: If the provided game_config does not have a valid Backend.
    """
    try:
        cfg = game_config or GameConfig()
        if cfg.backend is None:
            raise ValueError(
                "GameConfig.backend must be set to a Backend instance"
            )

        game = Game(cfg, scene_registry=scene_registry)
        game.run()
    # Justification: We need to catch all exceptions while we improve error handling.
    # pylint: disable=broad-exception-caught
    except Exception as e:
        logger.exception(f"Unhandled exception in game loop: {e}")
        logger.debug(traceback.format_exc())
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
    "Game",
    "GameConfig",
    "run_game",
]

__version__ = get_version()
