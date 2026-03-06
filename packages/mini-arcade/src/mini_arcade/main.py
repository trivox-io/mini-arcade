"""
Mini Arcade CLI entry point.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import mini_arcade.modules as commands_pkg
from mini_arcade.app import MiniArcadeCLI
from mini_arcade.cli.cli import CLIConfig, GlobalParserBuilder
from mini_arcade.constants import APP, CLI
from mini_arcade.utils.module_loader import load_command_packages


def main(argv: Optional[list[str]] = None):
    """
    Main entry point for the Mini Arcade CLI.

    :param argv: Optional list of command-line arguments. If None, uses sys.argv[1:].
    :type argv: Optional[list[str]]
    :raises SystemExit: Exits with the appropriate exit code after running the command.
    """
    if argv is None:
        argv = sys.argv[1:]

    global_parser = GlobalParserBuilder.build_global_parser(
        APP.version,
    )
    remaining_argv: list[str]
    _, remaining_argv = global_parser.parse_known_args(argv)

    commands_dir = Path(commands_pkg.__file__).parent

    load_command_packages(
        base_namespace="mini_arcade.modules",
        base_dir=commands_dir,
    )

    cli_app = MiniArcadeCLI(
        config=CLIConfig(
            app_name=CLI.executable_name,
            description=CLI.description,
            usage=CLI.usage,
            parents=[global_parser],
        ),
    )

    args = cli_app.parse_args(remaining_argv)
    exit_code = cli_app.run_command(args)
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
