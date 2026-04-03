"""
Canonical game command processors aligned with the stable target architecture.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from mini_arcade.cli.base_command_processor import BaseCommandProcessor
from mini_arcade.cli.exceptions import CommandException
from mini_arcade.commands.shared.base_target_locator import (
    BaseTargetLocator,
    TargetSpec,
)
from mini_arcade.commands.shared.process import run_child_process
from mini_arcade.commands.shared.process.command_builders import (
    GameCommandBuilder,
)
from mini_arcade.commands.shared.process.environment import (
    ExecutionEnvironmentBuilder,
    _build_pythonpath,
    _find_repo_root,
    _workspace_source_roots,
)
from mini_arcade.commands.shared.process.runner import (
    INTERRUPTED_EXIT_CODE,
    SubprocessRunner,
)
from mini_arcade.utils.logging import logger

from .game_locator import (
    GameLocator,
    TargetMetadataError,
    _load_tool_table,
    load_game_meta,
)
from .models import GameKwargs
from .scaffold import GameScaffoldProcessor, GameScaffoldSpec
from .target_resolver import TargetResolver


class BaseGameProcessor(BaseCommandProcessor):
    """
    Base processor for game commands, providing shared utilities.
    """

    def __init__(self):
        self._target_resolver = TargetResolver(self.kwargs)
        self._env_builder = ExecutionEnvironmentBuilder()
        self._command_builder = GameCommandBuilder()


def _stop_process(proc: subprocess.Popen) -> None:
    """
    Compatibility wrapper around the shared subprocess runner shutdown logic.
    """

    # Reuse the shared runner implementation to keep subprocess behavior
    # consistent across command domains.
    SubprocessRunner()._stop_process(proc)  # pylint: disable=protected-access


def _run_child_process(
    *,
    cmd: list[str],
    cwd: Path,
    env: dict[str, str],
) -> tuple[int, bool]:
    """
    Compatibility wrapper around the shared child-process runner.
    """

    return run_child_process(cmd=cmd, cwd=cwd, env=env)


class GameRunnerProcessor(BaseGameProcessor):
    """
    Runs one game using the reusable target resolver and process runner.
    """

    def __init__(self, **kwargs):
        self.kwargs = GameKwargs.from_dict(kwargs)
        super().__init__()

    def run(self):
        try:
            logger.debug("Running game...")
            spec = self._target_resolver.resolve()
            cmd = self._command_builder.build(
                spec,
                pass_through=self.kwargs.pass_through,
            )
            env = self._env_builder.build(spec)

            exit_code, interrupted = run_child_process(
                cmd=cmd,
                cwd=spec.root_dir,
                env=env,
            )

            if interrupted:
                logger.warning("Game run was interrupted by user (Ctrl+C).")

            return exit_code
        except ValueError as exc:
            raise CommandException(str(exc)) from exc


__all__ = [
    "INTERRUPTED_EXIT_CODE",
    "TargetMetadataError",
    "TargetSpec",
    "BaseTargetLocator",
    "GameLocator",
    "GameRunnerProcessor",
    "GameScaffoldProcessor",
    "GameScaffoldSpec",
    "TargetResolver",
    "load_game_meta",
    "_load_tool_table",
    "_find_repo_root",
    "_workspace_source_roots",
    "_build_pythonpath",
    "_stop_process",
    "_run_child_process",
]
