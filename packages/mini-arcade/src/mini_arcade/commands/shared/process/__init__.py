"""
Public shared subprocess helpers used by command processors.
"""

from __future__ import annotations

from pathlib import Path

from mini_arcade.commands.shared.process.models import ExecutionRequest
from mini_arcade.commands.shared.process.runner import SubprocessRunner

__all__ = ["run_child_process"]


def run_child_process(
    *,
    cmd: list[str],
    cwd: Path,
    env: dict[str, str],
) -> tuple[int, bool]:
    """
    Run one child process and return ``(exit_code, interrupted)``.
    """
    request = ExecutionRequest(
        cmd=cmd,
        cwd=cwd,
        env=env,
    )
    result = SubprocessRunner().run(request)
    return result.exit_code, result.interrupted
