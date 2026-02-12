"""
Pipeline for managing and executing systems in order.
Defines the SystemPipeline dataclass that holds and runs systems.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, Iterable, List

from mini_arcade_core.scenes.systems.base_system import (
    BaseSystem,
    TSystemContext,
)


@dataclass
class SystemPipeline(Generic[TSystemContext]):
    """
    Pipeline for managing and executing systems in order.

    :ivar systems (List[BaseSystem[TSystemContext]]): List of systems in the pipeline.
    """

    systems: List[BaseSystem[TSystemContext]] = field(default_factory=list)

    def add(self, system: BaseSystem[TSystemContext]):
        """
        Add a system to the pipeline and sort by order.

        :param system: The system to add.
        :type system: BaseSystem[TSystemContext]
        """
        self.systems.append(system)
        self.systems.sort(key=lambda s: getattr(s, "order", 0))

    def extend(self, systems: Iterable[BaseSystem[TSystemContext]]):
        """
        Extend the pipeline with multiple systems.

        :param systems: An iterable of systems to add.
        :type systems: Iterable[BaseSystem[TSystemContext]]
        """
        for s in systems:
            self.add(s)

    def step(self, ctx: TSystemContext):
        """
        Execute a step for each system in the pipeline.

        :param ctx: The system context.
        :type ctx: TSystemContext
        """
        for system in self.systems:
            if hasattr(system, "enabled") and not system.enabled(ctx):
                continue
            system.step(ctx)
