"""
Base command module
"""

from __future__ import annotations

from typing import List, Optional, Protocol, Tuple

from mini_arcade.cli.argument_type import ArgumentType


class CommandProtocol(Protocol):
    """

    :ivar name: Optional[str]: Command name (for registry); defaults to class name lowercased.
    :ivar aliases: Tuple[str, ...]: Optional command aliases.
    :ivar summary: Optional[str]: Short description of the command.
    :ivar epilog: Optional[str]: Additional help text for the command.
    :ivar args: Optional[List[ArgumentType]]: List of command arguments.
    :ivar abstract: bool: If True, the command is not registered (base class
    """

    # Metadata read by CommandRegistry.implementation(...)
    name: Optional[str]
    aliases: Tuple[str, ...] = ()
    summary: Optional[str]
    epilog: Optional[str]
    args: Optional[List[ArgumentType]]
    abstract: bool = False  # if True, decorator will skip registration

    @classmethod
    def define_arguments(cls) -> List[ArgumentType]:
        """
        Return the list of ArgumentType for this command.

        :return: List of ArgumentType instances.
        :rtype: List[ArgumentType]
        """

    def validate(self, **_kwargs):
        """Optional argument validation hook."""

    def _run(self, **kwargs):
        """Internal run (pre-exec)."""

    def _execute(self, **kwargs):
        """Internal execution step (core logic)."""

    def execute(self, **kwargs):
        """External command entrypoint."""
