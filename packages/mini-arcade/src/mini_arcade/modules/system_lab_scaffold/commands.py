"""
CLI command for scaffolding a minimal reusable system lab experiment.
"""

from __future__ import annotations

from mini_arcade.cli.argument_type import ArgumentType
from mini_arcade.cli.base_command import BaseCommand
from mini_arcade.cli.registry import CommandRegistry

from .processors import SystemLabScaffoldProcessor


@CommandRegistry.implementation("scaffold-system-lab")
class ScaffoldSystemLabCommand(BaseCommand):
    name = "scaffold-system-lab"
    aliases = ("new-system-lab", "scaffold-lab", "new-lab")
    args = [
        ArgumentType(
            "lab_id",
            str,
            "Experiment id in snake_case or kebab-case.",
            required=True,
        ),
        ArgumentType(
            "case_name",
            str,
            "Registered system lab case name. Defaults to normalized lab id.",
            required=False,
            default=None,
        ),
        ArgumentType(
            "title",
            str,
            "Human-friendly lab title. Defaults to title-cased lab id.",
            required=False,
            default=None,
        ),
        ArgumentType(
            "destination",
            str,
            "Parent directory where the new lab folder will be created. Defaults to ./experiments.",
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
    Scaffold a minimal reusable system lab experiment.

    Usage:
        mini-arcade scaffold-system-lab --lab-id sparks_lab
        mini-arcade scaffold-system-lab --lab-id sparks-lab --destination C:\\dev\\mini-arcade\\experiments
        mini-arcade scaffold-system-lab --lab-id sparks_lab --case-name spark_stats --dry-run
    """

    def _execute(self, **kwargs):
        self.set_processor(SystemLabScaffoldProcessor)
        return self._run(**kwargs)
