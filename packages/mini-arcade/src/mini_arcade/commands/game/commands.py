"""
Game command entrypoints aligned with the stable target architecture.
"""

from __future__ import annotations

from mini_arcade.cli.argument_type import ArgumentType
from mini_arcade.cli.base_command import BaseCommand
from mini_arcade.cli.registry import CommandRegistry
from mini_arcade.commands.shared.arguments import PassThroughArgument

from .processors import GameRunnerProcessor, GameScaffoldProcessor


@CommandRegistry.implementation("game")
class GameRunnerCommand(BaseCommand):
    is_group = True
    name = "game"
    args = [
        ArgumentType(
            "name",
            str,
            "Game kebab-case id/folder name (e.g. deja-bounce).",
            required=False,
            default=None,
        ),
        ArgumentType(
            "from_source",
            str,
            (
                "Parent folder where target games live "
                "(defaults to ./games when omitted)."
            ),
            required=False,
            default=None,
        ),
        PassThroughArgument(),
    ]

    __doc__ = """
    Run a game.

    Usage:
        mini-arcade game --name pong [--pass-through <args...>]
        mini-arcade game --name pong [--from-source <games_parent>] [--pass-through <args...>]
    """

    def _execute(self, **kwargs):
        self.set_processor(GameRunnerProcessor)
        self._run(**kwargs)


@CommandRegistry.implementation("game-scaffold")
class ScaffoldGameCommand(BaseCommand):
    name = "scaffold"
    parent = "game"
    aliases = ("new-game",)
    args = [
        ArgumentType(
            "id",
            str,
            "Game id in kebab-case (for example: my-first-game).",
            required=True,
        ),
        ArgumentType(
            "package",
            str,
            "Python package name in snake_case. Defaults to game-id normalized.",
            required=False,
            default=None,
        ),
        ArgumentType(
            "title",
            str,
            "Human-friendly game title. Defaults to title-cased game id.",
            required=False,
            default=None,
        ),
        ArgumentType(
            "destination",
            str,
            (
                "Parent directory where the new game folder will be created. "
                "Defaults to ./games."
            ),
            required=False,
            default=None,
        ),
        ArgumentType(
            "force",
            bool,
            "Overwrite scaffold files if the target folder already exists.",
            required=False,
            default=False,
        ),
        ArgumentType(
            "dry_run",
            bool,
            "Print the planned file tree without writing files.",
            required=False,
            default=False,
        ),
    ]

    __doc__ = """
    Scaffold a new runnable Mini Arcade game project.

    Usage:
        mini-arcade game scaffold --id my-first-game
        mini-arcade game scaffold --id my-first-game --destination C:\\dev\\arcade-forge\\games
        mini-arcade game scaffold --id my-first-game --package my_first_game --dry-run
    """

    def _execute(self, **kwargs):
        self.set_processor(GameScaffoldProcessor)
        return self._run(**kwargs)
