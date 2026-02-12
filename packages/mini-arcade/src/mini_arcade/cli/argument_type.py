"""
Argument Type Definitions for Mini Arcade CLI
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from typing import Callable, List, Optional, Type, Union

JSON = object()
DataType = Type[Union[str, int, float, bool]]


# pylint: disable=too-many-instance-attributes
@dataclass
class ArgumentType:
    """
    Represents an argument for a command.

    :ivar name (str): The name of the argument.
    :ivar data_type (DataType): The data type of the argument.
    :ivar help_text (str): The help text for the argument.
    :ivar required (bool): Whether the argument is required.
    :ivar default (Optional[DataType]): The default value for the argument.
    :ivar choices (Optional[List[str]]): The choices for the argument.
    :ivar nargs (Optional[Union[int, str]]): The number of arguments.
    :ivar metavar (Optional[str]): The metavar for the argument.
    :ivar env (Optional[str]): The environment variable associated with the argument.
    """

    name: str
    data_type: DataType
    help_text: str
    required: bool = False
    default: Optional[DataType] = None
    choices: Optional[List[str]] = None
    nargs: Optional[Union[int, str]] = None
    metavar: Optional[str] = None
    env: Optional[str] = None

    def to_dict(self) -> dict:
        """
        Convert the argument to a dictionary.

        :return: The argument as a dictionary.
        :rtype: dict
        """

        return asdict(self)


# pylint: enable=too-many-instance-attributes


def coerce_type(t: DataType) -> Callable[[str], DataType]:
    """
    Coerce a type to a callable that converts a string to that type.

    :param t: The type to coerce.
    :type t: DataType

    :return: A callable that converts a string to the specified type.
    :rtype: Callable[[str], DataType]
    """

    def _coerce_json(s):
        try:
            return json.loads(s)
        except json.JSONDecodeError as e:
            raise argparse.ArgumentTypeError(f"Invalid JSON: {e}")

    if t is JSON:
        return _coerce_json
    return t
