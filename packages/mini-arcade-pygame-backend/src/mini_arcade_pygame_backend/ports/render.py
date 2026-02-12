"""
Render port implementation for the pygame backend.
Provides functionality to draw shapes and manage rendering state.
"""

from __future__ import annotations

import pygame
from mini_arcade_core.backend.utils import (  # pyright: ignore[reportMissingImports]
    rgba,
)
from mini_arcade_core.backend.viewport import ViewportTransform

from mini_arcade_pygame_backend.ports.window import WindowPort  # type: ignore


class RenderPort:
    """
    Render port for the Mini Arcade native backend.

    :param native_backend: The native backend instance.
    :type native_backend: native.Backend
    :param vp: The viewport transform.
    :type vp: ViewportTransform
    """

    def __init__(
        self,
        window: WindowPort,
        vp: ViewportTransform,
        background_color=(0, 0, 0),
    ):
        self._w = window
        self._vp = vp
        self._clear = rgba(background_color)
        self._next_tex_id: int = 1
        self._textures: dict[int, pygame.Surface] = {}

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
        self._clear = (int(r), int(g), int(b), 255)

    def begin_frame(self):
        """Begin a new rendering frame."""
        r, g, b, _ = self._clear
        self._w.screen.fill((r, g, b))

    def end_frame(self):
        """End the current rendering frame."""
        pygame.display.flip()

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
        # IMPORTANT: the pipeline passes viewport_w/h and assumes viewport
        # transform has been applied.
        self._w.screen.set_clip(pygame.Rect(int(x), int(y), int(w), int(h)))

    def clear_clip_rect(self):
        """Clear the clipping rectangle."""
        self._w.screen.set_clip(None)

    # Justification: Many arguments needed for drawing
    # pylint: disable=too-many-arguments,too-many-positional-arguments
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
        r, g, b, _ = rgba(color)
        sx, sy = self._vp.map_xy(int(x), int(y))
        sw, sh = self._vp.map_wh(int(w), int(h))
        # alpha: pygame.draw supports alpha only if surface has per-pixel alpha;
        # simplest: ignore alpha for now, or use a temp surface if you really need it.
        pygame.draw.rect(
            self._w.screen, (r, g, b), pygame.Rect(sx, sy, sw, sh)
        )

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
        r, g, b, _ = rgba(color)
        sx1, sy1 = self._vp.map_xy(int(x1), int(y1))
        sx2, sy2 = self._vp.map_xy(int(x2), int(y2))
        pygame.draw.line(self._w.screen, (r, g, b), (sx1, sy1), (sx2, sy2))

    def create_texture_rgba(
        self,
        w: int,
        h: int,
        data: bytes | bytearray | memoryview,
        pitch: int = -1,
    ) -> int:
        """
        Create a texture from RGBA pixel data.

        :param w: The width of the texture.
        :type w: int
        :param h: The height of the texture.
        :type h: int
        :param data: The pixel data in RGBA format.
        :type data: bytes | bytearray | memoryview
        :param pitch: The number of bytes per row (including padding).
            If -1, rows are assumed to be tightly packed.
        :type pitch: int
        :return: The ID of the created texture.
        :rtype: int
        """
        w = int(w)
        h = int(h)
        if pitch <= 0:
            pitch = w * 4

        mv = memoryview(data)
        needed = h * pitch
        if mv.nbytes < needed:
            raise ValueError(
                f"create_texture_rgba: buffer too small ({mv.nbytes}) for h*pitch ({needed})"
            )

        # Fast path: tightly packed RGBA rows
        if pitch == w * 4:
            # frombuffer shares memory; copy() to detach from Python buffer lifetime
            surf = pygame.image.frombuffer(
                mv[:needed], (w, h), "RGBA"
            ).convert_alpha()
        else:
            # Slow path: repack rows (supports padded pitch)
            packed = bytearray(w * h * 4)
            for row in range(h):
                src0 = row * pitch
                src1 = src0 + (w * 4)
                dst0 = row * (w * 4)
                dst1 = dst0 + (w * 4)
                packed[dst0:dst1] = mv[src0:src1]
            surf = pygame.image.frombuffer(
                bytes(packed), (w, h), "RGBA"
            ).convert_alpha()

        tex_id = self._next_tex_id
        self._next_tex_id += 1
        self._textures[tex_id] = surf
        return tex_id

    def draw_texture(self, tex: int, x: int, y: int, w: int, h: int):
        """
        Draw a texture at the specified position and size.

        :param tex: The ID of the texture to draw.
        :type tex: int
        :param x: The x-coordinate of the top-left corner where the texture should be drawn.
        :type x: int
        :param y: The y-coordinate of the top-left corner where the texture should be drawn.
        :type y: int
        :param w: The width to draw the texture.
        :type w: int
        :param h: The height to draw the texture.
        :type h: int
        """
        surf = self._textures.get(int(tex))
        if surf is None:
            return

        sx, sy = self._vp.map_xy(int(x), int(y))
        sw, sh = self._vp.map_wh(int(w), int(h))

        if sw <= 0 or sh <= 0:
            return

        if surf.get_width() != sw or surf.get_height() != sh:
            scaled = pygame.transform.scale(surf, (sw, sh))
            self._w.screen.blit(scaled, (sx, sy))
        else:
            self._w.screen.blit(surf, (sx, sy))

    def destroy_texture(self, tex: int) -> None:
        """
        Destroy a texture, freeing associated resources.

        :param tex: The ID of the texture to destroy.
        :type tex: int
        """
        self._textures.pop(int(tex), None)

    def draw_texture_tiled_y(
        self, tex_id: int, x: int, y: int, w: int, h: int
    ):
        """
        Draw a texture repeated vertically to fill (w,h).
        Assumes you can resolve tex_id -> pygame.Surface, and supports scaling width.
        """
        surf = self._textures[tex_id]  # adapt to your texture store
        # Scale the tile to target width, keep tile height
        tile_h = surf.get_height()
        tile = pygame.transform.scale(surf, (int(w), int(tile_h)))

        cur_y = int(y)
        end_y = int(y + h)

        while cur_y < end_y:
            remaining = end_y - cur_y
            if remaining >= tile_h:
                self._w.screen.blit(tile, (int(x), cur_y))
                cur_y += tile_h
            else:
                # partial tile at the end
                partial = tile.subsurface(
                    pygame.Rect(0, 0, int(w), int(remaining))
                )
                self._w.screen.blit(partial, (int(x), cur_y))
                break
