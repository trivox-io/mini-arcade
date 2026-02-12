"""
Capture port implementation for Mini Arcade Native Backend.
Provides functionality to capture screenshots in BMP format.
"""

from __future__ import annotations

import pygame

from mini_arcade_pygame_backend.ports.window import WindowPort


class CapturePort:
    """
    Capture port for the Mini Arcade pygame backend.
    """

    def __init__(self, window: WindowPort):
        self._w = window

    def bmp(self, path: str) -> bool:
        """
        Capture the current screen and save it as a BMP file.

        :param path: The file path to save the BMP screenshot.
        :type path: str
        :return: True if the screenshot was successfully saved, False otherwise.
        :rtype: bool
        """
        if not path:
            return False
        pygame.image.save(self._w.screen, str(path))
        return True

    def argb8888_bytes(self) -> tuple[int, int, bytes]:
        """
        Capture the current screen and return the pixel data in ARGB8888 format.

        :return: A tuple containing the width, height, and pixel data in ARGB8888 format.
        :rtype: tuple[int, int, bytes]
        """
        w, h = self._w.screen.get_size()
        data = pygame.image.tostring(self._w.screen, "ARGB")
        return int(w), int(h), data
