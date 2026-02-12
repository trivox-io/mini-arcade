"""
Text port implementation for the native backend.
Provides functionality to draw and measure text.
"""

from __future__ import annotations

import pygame
from mini_arcade_core.backend.utils import (  # pyright: ignore[reportMissingImports]
    rgba,
)
from mini_arcade_core.backend.viewport import ViewportTransform

from mini_arcade_pygame_backend.ports.window import WindowPort


class TextPort:
    """
    Text port for the Mini Arcade native backend.

    :param native_backend: The native backend instance.
    :type native_backend: native.Backend
    :param vp: The viewport transform.
    :type vp: ViewportTransform
    :param font_path: The path to the font file to use for text rendering.
    :type font_path: str | None
    """

    def __init__(
        self,
        window: WindowPort,
        vp: ViewportTransform,
        font_path: str | None = None,
    ):
        self._w = window
        self._vp = vp
        self._font_path = font_path
        self._fonts: dict[int, pygame.font.Font] = {}

    def _font(self, font_size: int | None) -> pygame.font.Font:
        size = int(font_size or 24)
        size = max(8, size)
        cached = self._fonts.get(size)
        if cached:
            return cached

        if self._font_path:
            f = pygame.font.Font(self._font_path, size)
        else:
            f = pygame.font.Font(None, size)  # default font

        self._fonts[size] = f
        return f

    def measure(
        self, text: str, font_size: int | None = None
    ) -> tuple[int, int]:
        """
        Measure the width and height of the given text.

        :param text: The text to measure.
        :type text: str
        :param font_size: The font size to use for measurement.
        :type font_size: int | None
        :return: A tuple containing the width and height of the text.
        :rtype: tuple[int, int]
        """
        scaled_size = (
            None
            if font_size is None
            else max(8, int(round(font_size * self._vp.s)))
        )
        f = self._font(scaled_size)
        w_px, h_px = f.size(text)

        s = self._vp.s or 1.0
        return int(round(w_px / s)), int(round(h_px / s))

    # Justification: Many arguments needed for text drawing
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def draw(
        self,
        x: int,
        y: int,
        text: str,
        color=(255, 255, 255),
        font_size: int | None = None,
    ):
        """
        Draw the given text at the specified position.

        :param x: The x-coordinate to draw the text.
        :type x: int
        :param y: The y-coordinate to draw the text.
        :type y: int
        :param text: The text to draw.
        :type text: str
        :param color: The color of the text as an (R, G, B) or (R, G, B, A) tuple.
        :type color: tuple[int, int, int] | tuple[int, int, int, int]
        :param font_size: The font size to use for drawing.
        :type font_size: int | None
        """
        r, g, b, _ = rgba(color)
        sx, sy = self._vp.map_xy(int(x), int(y))

        scaled_size = (
            None
            if font_size is None
            else max(8, int(round(font_size * self._vp.s)))
        )
        f = self._font(scaled_size)

        surf = f.render(text, True, (r, g, b))
        self._w.screen.blit(surf, (sx, sy))
