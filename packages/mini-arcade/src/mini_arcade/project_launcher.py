"""
Helpers for project-local ``manage.py`` entrypoints.
"""

from __future__ import annotations

import sys
from collections.abc import Callable, Sequence


def run_project_entrypoint(
    local_run: Callable[[], object],
    argv: Sequence[str] | None = None,
) -> int:
    """
    Run a project-local entrypoint.

    With no args, launch the local project app.
    With any args, dispatch to the shared Mini Arcade CLI.
    """

    args = list(sys.argv[1:] if argv is None else argv)
    if args:
        # Justification: This import must stay lazy so project-local manage.py
        # can dispatch to the shared CLI without importing the local game app
        # and its runtime dependencies first.
        # pylint: disable=import-outside-toplevel
        from mini_arcade.main import main as cli_main

        cli_main(args)
        return 0

    result = local_run()
    return int(result) if isinstance(result, int) else 0


__all__ = ["run_project_entrypoint"]
