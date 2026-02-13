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

    # TODO: Implement this for sorting
    @staticmethod
    def insertion_sort(arr):
        """
        Sorts a list of elements using the Insertion Sort algorithm.
        """
        # Traverse through 1 to len(arr)
        for i in range(1, len(arr)):
            key = arr[i]
            # Move elements of arr[0..i-1], that are greater than key,
            # to one position ahead of their current position
            j = i - 1
            while j >= 0 and key < arr[j]:
                arr[j + 1] = arr[j]
                j -= 1
            arr[j + 1] = key
        return arr

    def add(self, system: BaseSystem[TSystemContext]):
        """
        Add a system to the pipeline and sort by order.

        :param system: The system to add.
        :type system: BaseSystem[TSystemContext]
        """
        self.systems.append(system)
        self.systems.sort(key=self._sort_key)

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

    def _sort_key(self, s: BaseSystem):
        return (
            getattr(s, "phase", 0),
            getattr(s, "order", 0),
            getattr(s, "name", s.__class__.__name__),
            s.__class__.__name__,
        )
