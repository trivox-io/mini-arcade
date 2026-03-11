"""
Bundle primitives for grouping scene systems without treating them as one system.
"""

from __future__ import annotations

from typing import Generic, Iterable, Protocol, runtime_checkable

from .base_system import BaseSystem, TSystemContext


@runtime_checkable
class SystemBundle(Protocol, Generic[TSystemContext]):
    """
    Structural contract for a bundle that expands into multiple systems.
    """

    def iter_systems(self) -> Iterable[BaseSystem[TSystemContext]]:
        """
        Return the concrete systems that should be added to the pipeline.
        """
