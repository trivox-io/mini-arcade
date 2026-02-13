"""
Protocol for base systems in the mini arcade core.
Defines the BaseSystem protocol that all systems should implement.
"""

from __future__ import annotations

from typing import Generic, Protocol, TypeVar, runtime_checkable

# Justification: Type variable name is conventional.
# pylint: disable=invalid-name
TSystemContext = TypeVar("TSystemContext")
# pylint: enable=invalid-name


@runtime_checkable
class BaseSystem(Protocol, Generic[TSystemContext]):
    """Protocol for a system that operates within a given context."""

    name: str
    phase: int = 0
    order: int = 0

    def enabled(self, ctx: TSystemContext) -> bool:
        """
        Determine if the system is enabled in the given context.

        :param ctx: The system context.
        :type ctx: TSystemContext

        :return: True if the system is enabled, False otherwise.
        :rtype: bool
        """
        return True

    def step(self, ctx: TSystemContext):
        """
        Perform a single step of the system within the given context.

        :param ctx: The system context.
        :type ctx: TSystemContext
        """
