"""
Game Runner Command: Implements the "run" command to start a Mini Arcade game or example.
"""

from __future__ import annotations

from mini_arcade.cli.argument_type import ArgumentType
from mini_arcade.cli.base_command import BaseCommand
from mini_arcade.cli.registry import CommandRegistry

from .processors import GameRunnerProcessor


@CommandRegistry.implementation("run")
class GameRunnerCommand(BaseCommand):
    name = "run"
    args = [
        ArgumentType(
            "game",
            str,
            "Game id/folder name (e.g. deja-bounce). Mutually exclusive with --example.",
            required=False,
            default=None,
        ),
        ArgumentType(
            "example",
            str,
            "Example id/folder path (e.g. config/engine_config_basics). Mutually exclusive with --game.",
            required=False,
            default=None,
        ),
        ArgumentType(
            "from_source",
            str,
            "Parent folder where games live (defaults to ./games in dev)",
            required=False,
            default=None,
        ),
        ArgumentType(
            "examples_dir",
            str,
            "Parent folder where examples live (defaults to ./examples in dev)",
            required=False,
            default=None,
        ),
        ArgumentType(
            "pass_through",
            str,
            "Args to forward to the target entrypoint. Use: --pass-through <args...>",
            required=False,
            nargs="...",
            default=[],
        ),
    ]

    __doc__ = """
    Run a game or an example.

    Usage:
        mini-arcade run --game deja-bounce [--from-source <games_parent>] [--pass-through <args...>]
        mini-arcade run --example config/engine_config_basics [--examples-dir <examples_parent>] [--pass-through <args...>]
    
    Description:
        This command starts a Mini Arcade game or example. You can specify the game/example by its id or folder name. By default, it looks for games in the ./games directory and examples in the ./examples directory (relative to the current working directory). You can override these defaults with the --from-source and --examples-dir options.
    """

    def _execute(self, **kwargs):
        self.set_processor(GameRunnerProcessor)
        self._run(**kwargs)
