"""
Example command models aligned with the stable target architecture.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from mini_arcade.commands.shared.pass_through_normalizer import (
    PassThroughNormalizer,
)

ExampleKwargsType = Union["ExampleKwargs", "ExampleTourKwargs"]
Kwargs = ExampleKwargsType


@dataclass
class ExampleKwargs:
    """
    Keyword arguments for the example command.

    :ivar id (str): The example id or folder path.
    :ivar examples_dir (str | None): Optional parent folder where examples live.
    :ivar pass_through (list[str]): Additional args forwarded to the entrypoint.
    """

    id: str
    examples_dir: str | None
    pass_through: list[str]

    @staticmethod
    def from_dict(kwargs: dict) -> "ExampleKwargs":
        """
        Build ``ExampleKwargs`` from parsed CLI kwargs.
        """
        return ExampleKwargs(
            id=kwargs["id"],
            examples_dir=kwargs.get("examples_dir"),
            pass_through=PassThroughNormalizer.normalize(
                kwargs.get("pass_through", [])
            ),
        )


@dataclass
class ExampleTourKwargs:
    """
    Keyword arguments for the example tour command.
    """

    examples_dir: str | None
    group: str | None
    from_example: str | None
    to_example: str | None
    stop_on_fail: bool
    list_only: bool
    pass_through: list[str]

    @staticmethod
    def from_dict(kwargs: dict) -> "ExampleTourKwargs":
        """
        Build ``ExampleTourKwargs`` from parsed CLI kwargs.
        """
        return ExampleTourKwargs(
            examples_dir=kwargs.get("examples_dir"),
            group=kwargs.get("group"),
            from_example=kwargs.get("from_example"),
            to_example=kwargs.get("to_example"),
            stop_on_fail=kwargs.get("stop_on_fail", False),
            list_only=kwargs.get("list_only", False),
            pass_through=PassThroughNormalizer.normalize(
                kwargs.get("pass_through", [])
            ),
        )


__all__ = [
    "ExampleKwargs",
    "ExampleKwargsType",
    "ExampleTourKwargs",
    "Kwargs",
]
