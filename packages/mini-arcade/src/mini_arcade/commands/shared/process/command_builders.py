"""
Defines the command builders for constructing the command-line arguments to execute
a game or example.
The builders take a resolved TargetSpec and produce the appropriate command to run it.
"""

from __future__ import annotations

import sys

from mini_arcade.commands.shared.base_target_locator import TargetSpec


class BaseCommandBuilder:
    def build(self, spec: TargetSpec, *, pass_through: list[str]) -> list[str]:
        raise NotImplementedError


class GameCommandBuilder(BaseCommandBuilder):
    def build(self, spec: TargetSpec, *, pass_through: list[str]) -> list[str]:
        return [sys.executable, str(spec.entrypoint), *pass_through]


class ExampleCommandBuilder(BaseCommandBuilder):
    def build(
        self,
        spec: TargetSpec,
        *,
        requested_example_id: str,
        pass_through: list[str],
    ) -> list[str]:
        return [
            sys.executable,
            str(spec.entrypoint),
            requested_example_id,
            *pass_through,
        ]
