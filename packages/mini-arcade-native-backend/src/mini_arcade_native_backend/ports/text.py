"""
Text port implementation for the native backend.
Provides functionality to draw and measure text.
"""

from __future__ import annotations

from collections import OrderedDict

from PIL import Image, ImageDraw, ImageFont

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
        fonts: dict[str, str | None] | None = None,
    ):
        self._b = native_backend
        self._vp = vp
        self._font_path = font_path
        self._font_paths: dict[str, str | None] = {"default": font_path}
        if fonts:
            self._font_paths.update(fonts)
        self._fonts_by_key: dict[tuple[str | None, int], int] = {}
        self._pil_fonts_by_key: dict[
            tuple[str | None, int], ImageFont.ImageFont
        ] = {}
        self._text_texture_cache: OrderedDict[
            tuple[str, tuple[int, int, int, int], int, str | None],
            tuple[int, int, int],
        ] = OrderedDict()
        self._max_cached_textures = 256

    def _resolve_font_path(self, font_name: str | None) -> str | None:
        if font_name is None:
            return self._font_paths.get("default", self._font_path)
        if font_name in self._font_paths:
            return self._font_paths[font_name]
        return self._font_paths.get("default", self._font_path)

    def _get_font_id(
        self, font_size: int | None, font_name: str | None
    ) -> int:
        font_path = self._resolve_font_path(font_name)
        if font_size is None or not font_path:
            return -1

        if font_size <= 0:
            raise ValueError(f"font_size must be > 0, got {font_size}")

        cache_key = (font_name, int(font_size))
        cached = self._fonts_by_key.get(cache_key)
        if cached is not None:
            return cached

        fid = self._b.load_font(font_path, int(font_size))
        self._fonts_by_key[cache_key] = fid
        return fid

    def _get_pil_font(
        self, font_size: int | None, font_name: str | None
    ) -> ImageFont.ImageFont:
        normalized_size = 24 if font_size is None else int(font_size)
        if normalized_size <= 0:
            normalized_size = 24

        cache_key = (font_name, normalized_size)
        cached = self._pil_fonts_by_key.get(cache_key)
        if cached is not None:
            return cached

        font_path = self._resolve_font_path(font_name)
        if font_path:
            font = ImageFont.truetype(font_path, normalized_size)
        else:
            font = ImageFont.load_default()
        self._pil_fonts_by_key[cache_key] = font
        return font

    def _measure_text_pixels(
        self,
        text: str,
        font_size: int | None,
        font_name: str | None,
    ) -> tuple[int, int, tuple[int, int, int, int]]:
        font = self._get_pil_font(font_size, font_name)
        bbox = font.getbbox(text or " ")
        width = max(1, int(bbox[2] - bbox[0]))
        height = max(1, int(bbox[3] - bbox[1]))
        return (
            width,
            height,
            (
                int(bbox[0]),
                int(bbox[1]),
                int(bbox[2]),
                int(bbox[3]),
            ),
        )

    def _evict_cached_textures_if_needed(self) -> None:
        while len(self._text_texture_cache) > self._max_cached_textures:
            _, (texture_id, _width, _height) = (
                self._text_texture_cache.popitem(last=False)
            )
            self._b.destroy_texture(int(texture_id))

    def _get_text_texture(
        self,
        text: str,
        color: tuple[int, int, int, int],
        font_size: int | None,
        font_name: str | None,
    ) -> tuple[int, int, int]:
        cache_key = (str(text), color, int(font_size or 24), font_name)
        cached = self._text_texture_cache.get(cache_key)
        if cached is not None:
            self._text_texture_cache.move_to_end(cache_key)
            return cached

        width, height, bbox = self._measure_text_pixels(
            text, font_size, font_name
        )
        font = self._get_pil_font(font_size, font_name)
        image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        drawer = ImageDraw.Draw(image)
        drawer.text(
            (-bbox[0], -bbox[1]),
            text,
            font=font,
            fill=color,
        )

        texture_id = int(
            self._b.create_texture_rgba(
                width,
                height,
                image.tobytes(),
                width * 4,
            )
        )
        cached = (texture_id, width, height)
        self._text_texture_cache[cache_key] = cached
        self._evict_cached_textures_if_needed()
        return cached

    def measure(
        self,
        text: str,
        font_size: int | None = None,
        font_name: str | None = None,
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
        w_px, h_px, _bbox = self._measure_text_pixels(
            text,
            scaled_size,
            font_name,
        )

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
        font_name: str | None = None,
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
        try:
            texture_id, width, height = self._get_text_texture(
                str(text),
                (r, g, b, a),
                scaled_size,
                font_name,
            )
        except OSError:
            font_id = self._get_font_id(scaled_size, font_name)
            self._b.draw_text(str(text), sx, sy, r, g, b, a, font_id)
            return

        self._b.draw_texture(
            int(texture_id),
            int(sx),
            int(sy),
            int(width),
            int(height),
        )
