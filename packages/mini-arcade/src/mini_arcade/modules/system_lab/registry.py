"""
Registry primitives for isolated system lab cases.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from mini_arcade.utils.implementation_registry import ImplementationRegistry


class BaseSystemLabCase(ABC):
    """
    Contract for one isolated system run scenario.
    """

    @abstractmethod
    def build_system(self) -> object:
        """
        Build the system instance to execute.
        """

    @abstractmethod
    def build_context(self) -> object:
        """
        Build the context passed into ``system.step(ctx)``.
        """

    def before_step(self, *, step_index: int, system: object, ctx: object) -> None:
        """
        Optional hook before each isolated step.
        """

    def after_step(self, *, step_index: int, system: object, ctx: object) -> None:
        """
        Optional hook after each isolated step.
        """

    def summarize(
        self,
        *,
        system: object,
        ctx: object,
        steps: int,
    ) -> dict[str, Any]:
        """
        Optional summary data appended to command output.
        """
        return {}

    def run_visual(self) -> int | None:
        """
        Optional interactive runner for visual/system-driven lab cases.
        """
        return None


class SystemLabRegistry(ImplementationRegistry[BaseSystemLabCase]):
    """
    Registry of named isolated system cases.
    """


SystemLabRegistry.implementation_base = BaseSystemLabCase


__all__ = ["BaseSystemLabCase", "SystemLabRegistry"]
