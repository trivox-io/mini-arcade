"""
Defines the data models for the execution request and result of a command processor.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExecutionRequest:
    cmd: list[str]
    cwd: Path
    env: dict[str, str]


@dataclass(frozen=True)
class ExecutionResult:
    exit_code: int
    interrupted: bool = False
