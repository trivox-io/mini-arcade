"""
Window port implementation for the native backend.
"""

from __future__ import annotations

# Justification: import from compiled extension module.
# pylint: disable=import-error,no-name-in-module
from mini_arcade_native_backend._native import (  # pyright: ignore[reportMissingModuleSource]
    Window,
)


class WindowPort:
    """
    Port for window management.

    :param native_window: The native window instance.
    :type native_window: Window
    """

    def __init__(self, native_window: Window):
        self._window = native_window
        self.refresh()

    def refresh(self):
        """Refresh cached window size values."""
        self.width, self.height = self.size()
        self.vp_width, self.vp_height = self.drawable_size()

    def set_title(self, title: str):
        """
        Set the window title.

        :param title: New window title.
        :type title: str
        """
        self._window.set_title(title)

    def resize(self, width: int, height: int):
        """
        Resize the window.

        :param width: New width in pixels.
        :type width: int
        :param height: New height in pixels.
        :type height: int
        """
        self._window.resize(int(width), int(height))

    def size(self) -> tuple[int, int]:
        """
        Get the window size.

        :return: Tuple of (width, height) in pixels.
        :rtype: tuple[int, int]
        """
        w, h = self._window.size()
        return int(w), int(h)

    def drawable_size(self) -> tuple[int, int]:
        """
        Get the drawable size of the window.

        :return: Tuple of (width, height) in pixels.
        :rtype: tuple[int, int]
        """
        w, h = self._window.drawable_size()
        return int(w), int(h)
