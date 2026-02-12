"""
Exceptions module for command errors.
"""

from __future__ import annotations

from typing import Literal

ExitCode = Literal[0, 1, 2]


class CommandException(Exception):
    """
    Exception for command errors.

    :cvar EXIT_CODE_MSG: Dict[ExitCode, str]: Mapping of exit codes to messages.
    """

    EXIT_CODE_MSG = {
        0: "Success",
        1: "General error",
        2: "Invalid command usage",
    }

    def __init__(self, message: str, exit_code: ExitCode = 2):
        """
        :param message: The error message.
        :type message: str

        :param exit_code: The exit code for the exception.
        :type exit_code: ExitCode
        """
        super().__init__(message)
        self.exit_code = exit_code
        self.exit_message = self.EXIT_CODE_MSG.get(exit_code, "Unknown error")
