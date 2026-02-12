"""
Service interfaces for runtime components.
"""

from __future__ import annotations

from typing import Protocol

from mini_arcade_core.engine.render.viewport import ViewportMode, ViewportState


class WindowPort(Protocol):
    """Interface for window-related operations."""

    def set_viewport_mode(self, mode: ViewportMode):
        """
        Set the viewport mode for rendering.

        :param mode: The viewport mode to set.
        :type mode: ViewportMode
        """

    def get_viewport(self) -> ViewportState:
        """
        Get the current viewport state.

        :return: The current ViewportState.
        :rtype: ViewportState
        """

    def screen_to_virtual(self, x: float, y: float) -> tuple[float, float]:
        """
        Convert screen coordinates to virtual coordinates.

        :param x: X coordinate on the screen.
        :type x: float

        :param y: Y coordinate on the screen.
        :type y: float

        :return: Corresponding virtual coordinates (x, y).
        :rtype: tuple[float, float]
        """

    def set_virtual_resolution(self, width: int, height: int):
        """
        Set the virtual resolution for rendering.

        :param width: Virtual width in pixels.
        :type width: int

        :param height: Virtual height in pixels.
        :type height: int
        """

    def set_title(self, title: str):
        """
        Set the window title.

        :param title: The new title for the window.
        :type title: str
        """

    def set_clear_color(self, r: int, g: int, b: int):
        """
        Set the clear color for the window.

        :param r: Red component (0-255).
        :type r: int

        :param g: Green component (0-255).
        :type g: int

        :param b: Blue component (0-255).
        :type b: int
        """

    def on_window_resized(self, width: int, height: int):
        """
        Handle window resized event.

        :param width: New width of the window.
        :type width: int

        :param height: New height of the window.
        :type height: int
        """

    def get_virtual_size(self) -> tuple[int, int]:
        """
        Get the current virtual resolution size.

        :return: Tuple of (virtual_width, virtual_height).
        :rtype: tuple[int, int]
        """
