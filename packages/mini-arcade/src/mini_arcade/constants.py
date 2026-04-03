"""
Mini Arcade Constants
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from mini_arcade.utils.codebase_length import CodebaseStats, codebase_length
from mini_arcade.utils.get_package_version import get_package_version

PACKAGE_NAME = "mini-arcade"

_PACKAGES = [
    "mini_arcade",
    "mini_arcade_core",
    "mini_arcade_pygame_backend",
    "mini_arcade_native_backend",
]


@dataclass(frozen=True)
class _App:
    version: str = get_package_version(PACKAGE_NAME)
    codebase: CodebaseStats = field(
        default_factory=lambda: codebase_length(_PACKAGES)
    )


@dataclass(frozen=True)
class _Cli:
    executable_name: str = PACKAGE_NAME
    description: str = "Mini Arcade CLI"
    usage: str = f"{PACKAGE_NAME} <command> [options]"


APP = _App()
CLI = _Cli()

ROOT_DIR = Path.cwd().resolve()
