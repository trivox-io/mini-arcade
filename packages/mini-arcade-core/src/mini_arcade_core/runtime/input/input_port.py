"""
Service interfaces for runtime components.
"""

from __future__ import annotations

from mini_arcade_core.backend.events import Event
from mini_arcade_core.runtime.input_frame import InputFrame


class InputPort:
    """Interface for input handling operations."""

    def build(
        self, events: list[Event], frame_index: int, dt: float
    ) -> InputFrame:
        """
        Build an InputFrame from the given events.

        :param events: List of input events.
        :type events: list[Event]

        :param frame_index: Current frame index.
        :type frame_index: int

        :param dt: Delta time since last frame.
        :type dt: float

        :return: Constructed InputFrame.
        :rtype: InputFrame
        """
