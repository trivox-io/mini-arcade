"""
CLI command for scaffolding a new Mini Arcade game project.
"""

from __future__ import annotations

from mini_arcade.cli.argument_type import ArgumentType
from mini_arcade.cli.base_command import BaseCommand
from mini_arcade.cli.registry import CommandRegistry

from .processors import GameScaffoldProcessor


@CommandRegistry.implementation("scaffold-game")
class ScaffoldGameCommand(BaseCommand):
    name = "scaffold-game"
    aliases = ("new-game",)
    args = [
        ArgumentType(
            "game_id",
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
            "Parent directory where the new game folder will be created. Defaults to ./originals, or ./games with --clone.",
            required=False,
            default=None,
        ),
        ArgumentType(
            "clone",
            bool,
            "Create the scaffold under ./games instead of ./originals.",
            required=False,
            default=False,
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
        mini-arcade scaffold-game --game-id my-first-game
        mini-arcade scaffold-game --game-id pong --clone
        mini-arcade scaffold-game --game-id my-first-game --destination C:\\dev\\arcade-forge\\originals
        mini-arcade scaffold-game --game-id my-first-game --package my_first_game --dry-run
    """

    def _execute(self, **kwargs):
        self.set_processor(GameScaffoldProcessor)
        return self._run(**kwargs)
