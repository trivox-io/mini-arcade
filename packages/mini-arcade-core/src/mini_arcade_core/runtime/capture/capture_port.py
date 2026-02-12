"""
Service interfaces for runtime components.
"""

from __future__ import annotations


class CapturePort:
    """Interface for frame capture operations."""

    def screenshot(self, label: str | None = None) -> str:
        """
        Capture the current frame.

        :param label: Optional label for the screenshot file.
        :type label: str | None

        :return: Screenshot file path.
        :rtype: str
        """

    def screenshot_bytes(self) -> bytes | None:
        """
        Capture the current frame and return it as bytes.

        :return: Screenshot data as bytes.
        :rtype: bytes | None
        """

    def screenshot_sim(
        self, run_id: str, frame_index: int, label: str = "frame"
    ) -> str:
        """
        Capture the current frame in a simulation context.

        :param run_id: Unique identifier for the simulation run.
        :type run_id: str

        :param frame_index: Index of the frame in the simulation.
        :type frame_index: int

        :param label: Optional label for the screenshot file.
        :type label: str

        :return: Screenshot file path.
        :rtype: str
        """
