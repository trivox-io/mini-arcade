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

    :ivar name (str): Game kebab-case id/folder name (e.g. deja-bounce).
    :ivar from_source (str | None): Optional parent folder where target games
        live. Defaults to ``./games`` when omitted.
    :ivar pass_through (list[str]): List of additional args to forward to the
        game entrypoint.
    """

    name: str
    from_source: str | None
    pass_through: list[str]

    @staticmethod
    def from_dict(kwargs: dict) -> GameKwargs:
        """
        Creates a GameKwargs instance from a dictionary of keyword arguments.

        :param kwargs: Dictionary of keyword arguments.
        :type kwargs: dict
        :return: A GameKwargs instance.
        :rtype: GameKwargs
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
    Keyword arguments for the scaffold command.

    :ivar id (str): Game id in kebab-case (for example: my-first-game).
    :ivar package (str | None): Python package name in snake_case. Defaults to game-id
        normalized.
    :ivar title (str | None): Human-friendly game title. Defaults to title-cased
        game id.
    :ivar destination (str | None): Parent directory where the new game folder will be
        created. Defaults to ``./games``.
    :ivar force (bool): Overwrite scaffold files if the target folder already exists.
    :ivar dry_run (bool): Print the planned file tree without writing files.
    """

    id: str
    package: str | None
    title: str | None
    destination: str | None
    force: bool
    dry_run: bool

    @staticmethod
    def from_dict(kwargs: dict) -> ScaffoldKwargs:
        """
        Creates a ScaffoldKwargs instance from a dictionary of keyword arguments.

        :param kwargs: Dictionary of keyword arguments.
        :type kwargs: dict
        :return: A ScaffoldKwargs instance.
        :rtype: ScaffoldKwargs
        """
        return ScaffoldKwargs(
            id=kwargs["id"],
            package=kwargs.get("package"),
            title=kwargs.get("title"),
            destination=kwargs.get("destination", GAMES_DIRNAME),
            force=bool(kwargs.get("force", False)),
            dry_run=bool(kwargs.get("dry_run", False)),
        )
