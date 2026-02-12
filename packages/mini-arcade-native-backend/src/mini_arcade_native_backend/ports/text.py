"""
Text port implementation for the native backend.
Provides functionality to draw and measure text.
"""

from __future__ import annotations

from mini_arcade_core.backend.utils import (  # pyright: ignore[reportMissingImports]
    rgba,
)
from mini_arcade_core.backend.viewport import ViewportTransform

# Justification: native is a compiled extension module.
# pylint: disable=no-name-in-module
from mini_arcade_native_backend import _native as native  # type: ignore

# Justification: Methods like draw have many parameters because of color and position.
# We want to keep the API simple and straightforward.
# pylint: disable=too-many-arguments,too-many-positional-arguments


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
        native_backend: native.Backend,
        vp: ViewportTransform,
        font_path: str | None,
    ):
        self._b = native_backend
        self._vp = vp
        self._font_path = font_path
        self._fonts_by_size: dict[int, int] = {}

    def _get_font_id(self, font_size: int | None) -> int:
        if font_size is None or not self._font_path:
            return -1

        if font_size <= 0:
            raise ValueError(f"font_size must be > 0, got {font_size}")

        cached = self._fonts_by_size.get(font_size)
        if cached is not None:
            return cached

        fid = self._b.load_font(self._font_path, int(font_size))
        self._fonts_by_size[font_size] = fid
        return fid

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
        font_id = self._get_font_id(scaled_size)
        w_px, h_px = self._b.measure_text(text, font_id)

        # Convert screen pixels back to virtual units for layout math
        s = self._vp.s or 1.0
        w_v = int(round(w_px / s))
        h_v = int(round(h_px / s))
        return w_v, h_v

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
        r, g, b, a = rgba(color)
        sx, sy = self._vp.map_xy(x, y)
        scaled_size = (
            None
            if font_size is None
            else max(8, int(round(font_size * self._vp.s)))
        )
        font_id = self._get_font_id(scaled_size)
        self._b.draw_text(text, sx, sy, r, g, b, a, font_id)
