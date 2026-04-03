"""
Example processors aligned with the stable target architecture.
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

    :ivar id (str): The example id or folder path (e.g. "config/engine_config_basics").
    :ivar examples_dir (str | None): Optional parent folder where examples live
        (defaults to "./examples/catalog" in dev).
    :ivar pass_through (list[str]): List of additional args to forward to the
        example entrypoint.
    """

    id: str
    examples_dir: str | None
    pass_through: list[str]

    @staticmethod
    def from_dict(kwargs: dict) -> ExampleKwargs:
        """
        Creates an ExampleKwargs instance from a dictionary of keyword arguments.

        :param kwargs: Dictionary of keyword arguments.
        :type kwargs: dict
        :return: An ExampleKwargs instance.
        :rtype: ExampleKwargs
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

    :ivar examples_dir (str | None): Optional parent folder where examples live
        (defaults to "./examples/catalog" in dev).
    :ivar group (str | None): Optional group id to filter examples
        (e.g. "config", "scene", "window").
    :ivar from_example (str | None): Optional example id to start the tour from.
    :ivar to_example (str | None): Optional example id to end the tour at.
    :ivar stop_on_fail (bool): Whether to stop the tour if an example fails
        (defaults to False).
    :ivar list_only (bool): Whether to only list the examples without running them
        (defaults to False).
    :ivar pass_through (list[str]): List of additional args to forward to the
        example entrypoint.
    """

    examples_dir: str | None
    group: str | None
    from_example: str | None
    to_example: str | None
    stop_on_fail: bool
    list_only: bool
    pass_through: list[str]

    @staticmethod
    def from_dict(kwargs: dict) -> ExampleTourKwargs:
        """
        Creates an ExampleTourKwargs instance from a dictionary of keyword arguments.

        :param kwargs: Dictionary of keyword arguments.
        :type kwargs: dict
        :return: An ExampleTourKwargs instance.
        :rtype: ExampleTourKwargs
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
