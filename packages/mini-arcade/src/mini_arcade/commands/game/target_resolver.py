"""
Target resolver for game commands. Resolves CLI args into validated target specs.
"""

from __future__ import annotations

from pathlib import Path

from mini_arcade.common.game_paths import GAMES_DIRNAME
from mini_arcade.utils.logging import logger
from mini_arcade.utils.paths import normalize_path
from mini_arcade.utils.repo import find_repo_root

from .game_locator import GameLocator
from .models import GameKwargs


class TargetResolver:
    """
    Resolves game CLI args into validated target specs.

    :param kwargs: The keyword arguments from the CLI command,
        expected to include ``name`` and optionally ``from_source``.
    :type kwargs: GameKwargs | None
    """

    def __init__(self, kwargs: GameKwargs | None = None):
        self.kwargs = kwargs
        repo_root = find_repo_root(Path.cwd())
        default_parent = (
            (repo_root / GAMES_DIRNAME).resolve()
            if repo_root is not None
            else (Path.cwd() / GAMES_DIRNAME).resolve()
        )
        self._locator = GameLocator(dev_default_parent_dir=default_parent)

    @property
    def parent_dir(self) -> Path:
        """
        Resolve the parent directory for games based on kwargs.

        :return: The parent directory for game discovery.
        :rtype: Path
        """
        if self.kwargs is None:
            raise ValueError(
                "TargetResolver requires kwargs to resolve parent_dir"
            )
        return self._locator.resolve_parent_dir(self.kwargs.from_source)

    def resolve(self):
        """
        Resolve the target game from the stored kwargs.
        """
        if self.kwargs is None:
            raise ValueError("TargetResolver requires kwargs to resolve")
        return self.resolve_id(self.kwargs.name)

    def resolve_id(self, game_id: str):
        """
        Resolve a target game id under the resolved parent directory.

        :param game_id: The game id to resolve.
        :type game_id: str
        :return: The validated target spec for the game.
        :rtype: TargetSpec
        """
        normalized_id = normalize_path(game_id)
        parent = self.parent_dir
        logger.debug(
            f"Resolving target game_id='{normalized_id}' under parent='{parent}'"
        )
        target_dir = self._locator.find_dir(parent, normalized_id)
        logger.debug(f"Found target directory: {target_dir}")
        return self._locator.validate(target_dir)


__all__ = ["TargetResolver"]
