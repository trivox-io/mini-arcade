"""
Render port implementation for the native backend.
Provides functionality to draw shapes and manage rendering state.
"""

from __future__ import annotations

from mini_arcade_core.backend.utils import (  # pyright: ignore[reportMissingImports]
    rgba,
)
from mini_arcade_core.backend.viewport import ViewportTransform

# Justification: native is a compiled extension module.
# pylint: disable=no-name-in-module
from mini_arcade_native_backend import _native as native  # type: ignore

# Justification: Methods like draw_rect have many parameters because of color and position.
# We want to keep the API simple and straightforward.
# pylint: disable=too-many-arguments,too-many-positional-arguments


class RenderPort:
    """
    Render port for the Mini Arcade native backend.

    :param native_backend: The native backend instance.
    :type native_backend: native.Backend
    :param vp: The viewport transform.
    :type vp: ViewportTransform
    """

    def __init__(self, native_backend: native.Backend, vp: ViewportTransform):
        self._b = native_backend
        self._vp = vp

    def set_clear_color(self, r: int, g: int, b: int):
        """
        Set the clear color for the renderer.

        :param r: Red component (0-255).
        :type r: int
        :param g: Green component (0-255).
        :type g: int
        :param b: Blue component (0-255).
        :type b: int
        """
        self._b.set_clear_color(int(r), int(g), int(b))

    def begin_frame(self):
        """Begin a new rendering frame."""
        self._b.begin_frame()

    def end_frame(self):
        """End the current rendering frame."""
        self._b.end_frame()

    def draw_rect(self, x: int, y: int, w: int, h: int, color=(255, 255, 255)):
        """
        Draw a filled rectangle.

        :param x: The x-coordinate of the rectangle.
        :type x: int
        :param y: The y-coordinate of the rectangle.
        :type y: int
        :param w: The width of the rectangle.
        :type w: int
        :param h: The height of the rectangle.
        :type h: int
        :param color: The color of the rectangle as an (R, G, B) or (R, G, B, A) tuple.
        :type color: tuple[int, int, int] | tuple[int, int, int, int]
        """
        r, g, b, a = rgba(color)
        sx, sy = self._vp.map_xy(x, y)
        sw, sh = self._vp.map_wh(w, h)
        self._b.draw_rect(sx, sy, sw, sh, r, g, b, a)

    def draw_line(
        self, x1: int, y1: int, x2: int, y2: int, color=(255, 255, 255)
    ):
        """
        Draw a line between two points.

        :param x1: The x-coordinate of the start point.
        :type x1: int
        :param y1: The y-coordinate of the start point.
        :type y1: int
        :param x2: The x-coordinate of the end point.
        :type x2: int
        :param y2: The y-coordinate of the end point.
        :type y2: int
        :param color: The color of the line as an (R, G, B) or (R, G, B, A) tuple.
        :type color: tuple[int, int, int] | tuple[int, int, int, int]
        """
        r, g, b, a = rgba(color)
        sx1, sy1 = self._vp.map_xy(x1, y1)
        sx2, sy2 = self._vp.map_xy(x2, y2)
        self._b.draw_line(sx1, sy1, sx2, sy2, r, g, b, a)

    def set_clip_rect(self, x: int, y: int, w: int, h: int):
        """
        Set the clipping rectangle.

        :param x: The x-coordinate of the clipping rectangle.
        :type x: int
        :param y: The y-coordinate of the clipping rectangle.
        :type y: int
        :param w: The width of the clipping rectangle.
        :type w: int
        :param h: The height of the clipping rectangle.
        :type h: int
        """
        sx, sy = self._vp.map_xy(x, y)
        sw, sh = self._vp.map_wh(w, h)
        self._b.set_clip_rect(sx, sy, sw, sh)

    def clear_clip_rect(self):
        """Clear the clipping rectangle."""
        self._b.clear_clip_rect()

    def create_texture_rgba(
        self, w: int, h: int, pixels: bytes, pitch: int | None = None
    ) -> int:
        """
        Create a texture from RGBA pixel data.

        :param w: The width of the texture.
        :type w: int
        :param h: The height of the texture.
        :type h: int
        :param pixels: The pixel data in RGBA format.
        :type pixels: bytes
        :param pitch: The number of bytes in a row of pixel data. If None, defaults to w * 4.
        :type pitch: int | None
        """
        if pitch is None:
            pitch = w * 4
        return int(
            self._b.create_texture_rgba(int(w), int(h), pixels, int(pitch))
        )

    def destroy_texture(self, tex: int) -> None:
        """
        Destroy a texture.

        :param tex: The texture ID to destroy.
        :type tex: int
        """
        self._b.destroy_texture(int(tex))

    def draw_texture(self, tex: int, x: int, y: int, w: int, h: int):
        """
        Draw a texture at the specified position and size.

        :param tex: The texture ID.
        :type tex: int
        :param x: The x-coordinate to draw the texture.
        :type x: int
        :param y: The y-coordinate to draw the texture.
        :type y: int
        :param w: The width to draw the texture.
        :type w: int
        :param h: The height to draw the texture.
        :type h: int
        """
        sx, sy = self._vp.map_xy(x, y)
        sw, sh = self._vp.map_wh(w, h)
        self._b.draw_texture(int(tex), int(sx), int(sy), int(sw), int(sh))

    def draw_texture_tiled_y(self, tex: int, x: int, y: int, w: int, h: int):
        """
        Draw a texture tiled vertically at the specified position and size.

        :param tex: The texture ID.
        :type tex: int
        :param x: The x-coordinate to draw the texture.
        :type x: int
        :param y: The y-coordinate to draw the texture.
        :type y: int
        :param w: The width to draw the texture.
        :type w: int
        :param h: The height to draw the texture.
        :type h: int
        """
        sx, sy = self._vp.map_xy(x, y)
        sw, sh = self._vp.map_wh(w, h)
        self._b.draw_texture_tiled_y(
            int(tex), int(sx), int(sy), int(sw), int(sh)
        )
