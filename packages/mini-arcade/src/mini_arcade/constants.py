"""
Mini Arcade Constants
"""

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade.utils.get_package_version import get_package_version

PACKAGE_NAME = "mini-arcade"


@dataclass(frozen=True)
class _App:
    version: str = get_package_version(PACKAGE_NAME)


@dataclass(frozen=True)
class _Cli:
    executable_name: str = PACKAGE_NAME
    description: str = "Mini Arcade CLI"
    usage: str = f"{PACKAGE_NAME} <command> [options]"


APP = _App()
CLI = _Cli()
