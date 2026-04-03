"""
Game command models aligned with the stable target architecture.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from mini_arcade.commands.shared.pass_through_normalizer import (
    PassThroughNormalizer,
)
from mini_arcade.common.game_paths import GAMES_DIRNAME

GameKwargsType = Union["GameKwargs", "ScaffoldKwargs"]


@dataclass
class GameKwargs:
    """
    Keyword arguments for game commands.
    """

    name: str
    from_source: str | None
    pass_through: list[str]

    @staticmethod
    def from_dict(kwargs: dict) -> "GameKwargs":
        """
        Build ``GameKwargs`` from parsed CLI kwargs.
        """
        return GameKwargs(
            name=kwargs["name"],
            from_source=kwargs.get("from_source"),
            pass_through=PassThroughNormalizer.normalize(
                kwargs.get("pass_through", [])
            ),
        )


@dataclass
class ScaffoldKwargs:
    """
    Keyword arguments for the game scaffold command.
    """

    id: str
    package: str | None
    title: str | None
    destination: str | None
    force: bool
    dry_run: bool

    @staticmethod
    def from_dict(kwargs: dict) -> "ScaffoldKwargs":
        """
        Build ``ScaffoldKwargs`` from parsed CLI kwargs.
        """
        return ScaffoldKwargs(
            id=kwargs["id"],
            package=kwargs.get("package"),
            title=kwargs.get("title"),
            destination=kwargs.get("destination", GAMES_DIRNAME),
            force=bool(kwargs.get("force", False)),
            dry_run=bool(kwargs.get("dry_run", False)),
        )


__all__ = [
    "GameKwargs",
    "GameKwargsType",
    "ScaffoldKwargs",
]
