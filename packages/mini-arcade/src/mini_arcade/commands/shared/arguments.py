"""
Shared argument definitions for mini-arcade commands.
"""

from __future__ import annotations

from mini_arcade.cli.argument_type import ArgumentType


class PassThroughArgument(ArgumentType):
    """
    Argument definition for forwarding remaining args to a child entrypoint.
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


__all__ = ["PassThroughArgument"]
