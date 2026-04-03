"""
Builders for command lines used to launch games and examples.
"""

from __future__ import annotations

import sys
from typing import Any

from mini_arcade.commands.shared.base_target_locator import TargetSpec


class BaseCommandBuilder:
    """
    Base class for converting a resolved target into a subprocess command.
    """

    def build(self, spec: TargetSpec, **kwargs: Any) -> list[str]:
        """
        Build the command line for a resolved target.
        """
        del spec, kwargs
        raise NotImplementedError


class GameCommandBuilder(BaseCommandBuilder):
    """
    Build the subprocess command for a game target.
    """

    def build(self, spec: TargetSpec, **kwargs: Any) -> list[str]:
        pass_through = list(kwargs.get("pass_through", []))
        return [sys.executable, str(spec.entrypoint), *pass_through]


class ExampleCommandBuilder(BaseCommandBuilder):
    """
    Build the subprocess command for an example target.
    """

    def build(self, spec: TargetSpec, **kwargs: Any) -> list[str]:
        requested_example_id = str(kwargs["requested_example_id"])
        pass_through = list(kwargs.get("pass_through", []))
        return [
            sys.executable,
            str(spec.entrypoint),
            requested_example_id,
            *pass_through,
        ]
