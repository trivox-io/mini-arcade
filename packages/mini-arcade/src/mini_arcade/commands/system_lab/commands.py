"""
CLI commands for listing, running, or scaffolding isolated system cases.
"""

from __future__ import annotations

from mini_arcade.cli.argument_type import ArgumentType
from mini_arcade.cli.base_command import BaseCommand
from mini_arcade.cli.exceptions import CommandException
from mini_arcade.cli.registry import CommandRegistry

from .processors import SystemRunnerProcessor, SystemScaffoldProcessor


@CommandRegistry.implementation("system")
class SystemCommand(BaseCommand):
    name = "system"
    is_group = True
    aliases = ("system-lab", "run-system")
    args = [
        ArgumentType(
            "module",
            str,
            "Registry module(s) to import before listing or running cases.",
            required=False,
            nargs="+",
            default=[],
        ),
        ArgumentType(
            "case",
            str,
            "Registered system case name to execute.",
            required=False,
            default=None,
        ),
        ArgumentType(
            "list",
            bool,
            "List registered cases and exit.",
            required=False,
            default=False,
        ),
        ArgumentType(
            "steps",
            int,
            "How many times to call system.step(ctx).",
            required=False,
            default=1,
        ),
        ArgumentType(
            "json",
            bool,
            "Emit machine-readable JSON summary output.",
            required=False,
            default=False,
        ),
        ArgumentType(
            "visual",
            bool,
            (
                "Launch the case's interactive visual runner "
                "instead of stepping it headlessly."
            ),
            required=False,
            default=False,
        ),
        ArgumentType(
            "backend",
            str,
            (
                "Override the visual runner backend provider "
                "(for example: pygame or native)."
            ),
            required=False,
            default=None,
        ),
    ]

    __doc__ = """
    List or run isolated system cases.

    Usage:
        mini-arcade system --module my_game.debug.system_lab --list
        mini-arcade system --module my_game.debug.system_lab --case ship_move --steps 3
        mini-arcade system --module my_game.debug.system_lab --visual --backend native
    """

    def validate(self, **kwargs):
        modules = kwargs.get("module") or []
        if not modules:
            raise CommandException(
                "system requires at least one --module to import cases"
            )
        if (
            not kwargs.get("list")
            and not kwargs.get("case")
            and not kwargs.get("visual")
        ):
            raise CommandException(
                "system requires --case <name>, --list, or --visual"
            )
        if kwargs.get("list") and kwargs.get("visual"):
            raise CommandException("--visual cannot be combined with --list")
        if kwargs.get("backend") and not kwargs.get("visual"):
            raise CommandException("--backend requires --visual")
        if int(kwargs.get("steps", 1)) < 1:
            raise CommandException("--steps must be >= 1")

    def _execute(self, **kwargs):
        self.set_processor(SystemRunnerProcessor)
        return self._run(**kwargs)


@CommandRegistry.implementation("system-scaffold")
class ScaffoldSystemCommand(BaseCommand):
    name = "scaffold"
    parent = "system"
    aliases = ("new-system", "new-system-lab", "scaffold-lab", "new-lab")
    args = [
        ArgumentType(
            "id",
            str,
            "Experiment id in snake_case or kebab-case.",
            required=True,
        ),
        ArgumentType(
            "case_name",
            str,
            "Registered system case name. Defaults to normalized id.",
            required=False,
            default=None,
        ),
        ArgumentType(
            "title",
            str,
            "Human-friendly experiment title. Defaults to title-cased id.",
            required=False,
            default=None,
        ),
        ArgumentType(
            "destination",
            str,
            (
                "Parent directory where the new experiment folder "
                "will be created. Defaults to ./experiments."
            ),
            required=False,
            default="experiments",
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
    Scaffold a minimal reusable system experiment.

    Usage:
        mini-arcade system scaffold --id sparks_lab
        mini-arcade system scaffold --id sparks-lab --destination C:\\dev\\mini-arcade\\experiments
        mini-arcade system scaffold --id sparks_lab --case-name spark_stats --dry-run
    """

    def _execute(self, **kwargs):
        self.set_processor(SystemScaffoldProcessor)
        return self._run(**kwargs)


SystemLabCommand = SystemCommand
ScaffoldSystemLabCommand = ScaffoldSystemCommand


__all__ = [
    "SystemCommand",
    "ScaffoldSystemCommand",
    "SystemLabCommand",
    "ScaffoldSystemLabCommand",
]
