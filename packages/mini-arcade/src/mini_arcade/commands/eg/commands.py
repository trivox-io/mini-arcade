"""
Example command entrypoints aligned with the stable target architecture.
"""

from __future__ import annotations

from mini_arcade.cli.argument_type import ArgumentType
from mini_arcade.cli.base_command import BaseCommand
from mini_arcade.cli.registry import CommandRegistry
from mini_arcade.commands.shared.arguments import PassThroughArgument

from .processors import ExampleRunnerProcessor, ExamplesTourProcessor


class ExamplesDirArgument(ArgumentType):
    """
    Custom argument type for specifying the examples directory.
    """

    def __init__(self):
        super().__init__(
            name="examples_dir",
            data_type=str,
            help_text=(
                "Parent folder where examples live (defaults to ./examples/catalog in dev)."
            ),
            required=False,
            default=None,
        )


@CommandRegistry.implementation("eg")
class ExampleRunnerCommand(BaseCommand):
    name = "eg"
    is_group = True
    aliases = ("example",)
    args = [
        ArgumentType(
            "id",
            str,
            "Example id/folder path (e.g. config/engine_config_basics).",
            required=False,
        ),
        ExamplesDirArgument(),
        PassThroughArgument(),
    ]

    __doc__ = """
    Run an example.

    Usage:
        mini-arcade eg --id config/engine_config_basics
        mini-arcade eg --id scene/minimal_scene --pass-through --backend native
    """

    def _execute(self, **kwargs):
        self.set_processor(ExampleRunnerProcessor)
        return self._run(**kwargs)


@CommandRegistry.implementation("eg-tour")
class TourCommand(BaseCommand):
    name = "tour"
    parent = "eg"
    args = [
        ExamplesDirArgument(),
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
        PassThroughArgument(),
    ]

    __doc__ = """
    Run catalog examples sequentially.

    Usage:
        mini-arcade eg tour
        mini-arcade eg tour --group scene
        mini-arcade eg tour --from-example scene/minimal_scene --to-example scene/pause_overlay_policy
        mini-arcade eg tour --pass-through --backend native
    """

    def _execute(self, **kwargs):
        self.set_processor(ExamplesTourProcessor)
        return self._run(**kwargs)
