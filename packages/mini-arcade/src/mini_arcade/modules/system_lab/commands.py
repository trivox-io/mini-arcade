"""
CLI command for listing or running isolated system lab cases.
"""

from __future__ import annotations

from mini_arcade.cli.argument_type import ArgumentType
from mini_arcade.cli.base_command import BaseCommand
from mini_arcade.cli.exceptions import CommandException
from mini_arcade.cli.registry import CommandRegistry

from .processors import SystemLabProcessor


@CommandRegistry.implementation("system-lab")
class SystemLabCommand(BaseCommand):
    name = "system-lab"
    aliases = ("run-system",)
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
            "Registered system lab case name to execute.",
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
            "Launch the case's interactive visual runner instead of stepping it headlessly.",
            required=False,
            default=False,
        ),
    ]

    __doc__ = """
    List or run isolated system lab cases.

    Usage:
        mini-arcade system-lab --module my_game.debug.system_lab --list
        mini-arcade system-lab --module my_game.debug.system_lab --case ship_move --steps 3
    """

    def validate(self, **kwargs):
        modules = kwargs.get("module") or []
        if not modules:
            raise CommandException(
                "system-lab requires at least one --module to import cases"
            )
        if (
            not kwargs.get("list")
            and not kwargs.get("case")
            and not kwargs.get("visual")
        ):
            raise CommandException(
                "system-lab requires --case <name>, --list, or --visual"
            )
        if kwargs.get("list") and kwargs.get("visual"):
            raise CommandException("--visual cannot be combined with --list")
        if int(kwargs.get("steps", 1)) < 1:
            raise CommandException("--steps must be >= 1")

    def _execute(self, **kwargs):
        self.set_processor(SystemLabProcessor)
        return self._run(**kwargs)
