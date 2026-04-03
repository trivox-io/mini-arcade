"""
Data models for shared subprocess execution helpers.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExecutionRequest:
    """
    One subprocess execution request.
    """

    cmd: list[str]
    cwd: Path
    env: dict[str, str]


@dataclass(frozen=True)
class ExecutionResult:
    """
    One subprocess execution result.
    """

    exit_code: int
    interrupted: bool = False
