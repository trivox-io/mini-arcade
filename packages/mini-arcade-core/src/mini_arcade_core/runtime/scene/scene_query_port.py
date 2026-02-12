"""
Scene query port protocol.
"""

from __future__ import annotations

from typing import Protocol, Sequence, runtime_checkable

from mini_arcade_core.engine.scenes.models import SceneEntry


@runtime_checkable
class SceneQueryPort(Protocol):
    """Read-only queries over the engine scene stack."""

    def visible_entries(self) -> Sequence[SceneEntry]:
        """
        Scenes that should be rendered (policy-aware).

        :return: Sequence of SceneEntry instances that are visible.
        :rtype: Sequence[SceneEntry]
        """

    def input_entry(self) -> SceneEntry | None:
        """
        The scene that currently receives input (top-most eligible).

        :return: SceneEntry that receives input, or None if stack is empty.
        :rtype: SceneEntry | None
        """

    def stack_summary(self) -> list[str]:
        """
        Convenience: human-readable stack lines for debug overlays.

        :return: List of strings summarizing the scene stack.
        :rtype: list[str]
        """
