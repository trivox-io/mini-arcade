"""
Window port implementation for the pygame backend.
"""

from __future__ import annotations

import pygame


class WindowPort:
    """
    Port for window management.
    """

    _title: str
    _resizeable: bool
    _flags: int
    width: int
    height: int

    def __init__(self, width: int, height: int, title: str, resizable: bool):
        """
        :param native_window: The native window instance.
        :type native_window: Window
        """
        self._title = title
        self._resizeable = resizable
        self._flags = pygame.RESIZABLE if resizable else 0

        self.screen = pygame.display.set_mode((width, height), self._flags)
        pygame.display.set_caption(title)

        self.width = width
        self.height = height

    def set_title(self, title: str):
        """
        Set the window title.

        :param title: New window title.
        :type title: str
        """
        self._title = title
        pygame.display.set_caption(title)

    def resize(self, width: int, height: int):
        """
        Resize the window.

        :param width: New width in pixels.
        :type width: int
        :param height: New height in pixels.
        :type height: int
        """
        self.width = int(width)
        self.height = int(height)
        self.screen = pygame.display.set_mode(
            (self.width, self.height), self._flags
        )

    def size(self) -> tuple[int, int]:
        """
        Get the window size.

        :return: Tuple of (width, height) in pixels.
        :rtype: tuple[int, int]
        """
        w, h = self.screen.get_size()
        self.width, self.height = int(w), int(h)
        return self.width, self.height

    def drawable_size(self) -> tuple[int, int]:
        """
        Get the drawable size of the window.

        :return: Tuple of (width, height) in pixels.
        :rtype: tuple[int, int]
        """
        return self.size()
