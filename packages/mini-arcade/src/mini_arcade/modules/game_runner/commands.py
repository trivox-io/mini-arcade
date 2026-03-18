"""
Game Runner Command: Implements the "run" command to start a Mini Arcade game or example.
"""

from __future__ import annotations

from mini_arcade.cli.argument_type import ArgumentType
from mini_arcade.cli.base_command import BaseCommand
from mini_arcade.cli.registry import CommandRegistry

from .processors import ExamplesTourProcessor, GameRunnerProcessor


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
            (
                "Example id/folder path (e.g. config/engine_config_basics). "
                "Mutually exclusive with --game.",
            ),
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
        mini-arcade run tour [tour options...]
    
    Description:
        This command starts a Mini Arcade game or example. You can specify the game/example by its id or folder name. By default, it looks for games in the ./games directory and examples in the ./examples directory (relative to the current working directory). You can override these defaults with the --from-source and --examples-dir options.
        It also supports the compatibility form `mini-arcade run tour`, which
        routes to the tutorial tour command.
    """

    def _execute(self, **kwargs):
        self.set_processor(GameRunnerProcessor)
        self._run(**kwargs)


@CommandRegistry.implementation("tour")
class TourCommand(BaseCommand):
    name = "tour"
    args = [
        ArgumentType(
            "examples_dir",
            str,
            "Parent folder where examples live (defaults to ./examples/catalog in dev)",
            required=False,
            default=None,
        ),
        ArgumentType(
            "group",
            str,
            "Optional group prefix filter (e.g. config, scene, window).",
            required=False,
            default=None,
        ),
        ArgumentType(
            "from_example",
            str,
            "Optional starting example id (inclusive).",
            required=False,
            default=None,
        ),
        ArgumentType(
            "to_example",
            str,
            "Optional ending example id (inclusive).",
            required=False,
            default=None,
        ),
        ArgumentType(
            "stop_on_fail",
            bool,
            "Stop at first failing example (default: keep going).",
            required=False,
            default=False,
        ),
        ArgumentType(
            "list_only",
            bool,
            "List resolved example order and exit.",
            required=False,
            default=False,
        ),
        ArgumentType(
            "pass_through",
            str,
            "Args forwarded to each example entrypoint. Use: --pass-through <args...>",
            required=False,
            nargs="...",
            default=[],
        ),
    ]

    __doc__ = """
    Run catalog examples sequentially.

    Usage:
        mini-arcade run tour
        mini-arcade run tour --group scene
        mini-arcade run tour --from-example scene/minimal_scene --to-example scene/pause_overlay_policy
        mini-arcade run tour --pass-through --backend native

    Description:
        This command orchestrates a full "run-all" tutorial session by launching
        examples one-by-one in subprocesses. When one example window closes, the
        next example starts automatically. Press Ctrl+C to stop the tour at
        any time.
    """

    def _execute(self, **kwargs):
        self.set_processor(ExamplesTourProcessor)
        self._run(**kwargs)
