"""
Base command processor Module
This module defines the BaseCommandProcessor class, which serves as a base for all
command processors in the application.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseCommandProcessor(ABC):
    """
    Base command processor class
    """

    @abstractmethod
    def run(self) -> Optional[Any]:
        """
        Run the command processor.

        :return: Optional result of the command execution.
        :rtype: Optional[Any]
        """
