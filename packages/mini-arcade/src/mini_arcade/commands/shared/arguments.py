"""
Shared argument definitions for mini-arcade commands.
"""

from __future__ import annotations

from mini_arcade.cli.argument_type import ArgumentType


class PassThroughArgument(ArgumentType):
    """
    Custom argument type for pass-through args that forwards all remaining args as a list.
    """

    def __init__(self):
        super().__init__(
            name="pass_through",
            data_type=str,
            help_text=(
                "Args forwarded to the target entrypoint. "
                "Use: --pass-through <args...>"
            ),
            required=False,
            nargs="...",
            default=[],
        )
