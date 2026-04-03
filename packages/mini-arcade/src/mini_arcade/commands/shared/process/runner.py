"""
Subprocess execution helpers for command processors.
"""

from __future__ import annotations

import subprocess
import time

from mini_arcade.commands.shared.process.models import (
    ExecutionRequest,
    ExecutionResult,
)

INTERRUPTED_EXIT_CODE = 130


class SubprocessRunner:
    """
    Encapsulates subprocess lifecycle handling.
    """

    def run(self, request: ExecutionRequest) -> ExecutionResult:
        """
        Run one subprocess request until completion or interruption.
        """
        with subprocess.Popen(
            request.cmd,
            cwd=str(request.cwd),
            env=request.env,
        ) as proc:
            try:
                while True:
                    code = proc.poll()
                    if code is not None:
                        return ExecutionResult(exit_code=int(code or 0))
                    time.sleep(0.1)
            except KeyboardInterrupt:
                self._stop_process(proc)
                return ExecutionResult(
                    exit_code=INTERRUPTED_EXIT_CODE,
                    interrupted=True,
                )

    def _stop_process(self, proc: subprocess.Popen) -> None:
        """
        Stop a running subprocess with graceful termination first.
        """
        if proc.poll() is not None:
            return

        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=3)
