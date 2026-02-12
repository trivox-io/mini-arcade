"""
Render service definition.
"""

from __future__ import annotations

from typing import Protocol

from mini_arcade_core.backend.backend import Backend
from mini_arcade_core.engine.render.context import RenderStats


class RenderServicePort(Protocol):
    """
    Render Service.
    This service manages rendering statistics and state.

    :ivar last_frame_ms (float): Time taken for the last frame in milliseconds.
    :ivar last_stats (RenderStats): Rendering statistics from the last frame.
    """

    backend: Backend
    last_frame_ms: float
    last_stats: RenderStats

    def load_texture(self, path: str) -> int:
        """
        Load a texture from a file path and return its texture ID.

        :param path: The file path to the texture image.
        :type path: str
        :return: The texture ID assigned by the backend.
        :rtype: int
        """

    # Justification: Disabling too-many-arguments for this method since it's a simple
    # wrapper around a backend call, and the arguments are all necessary for the tiling
    # functionality.
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def draw_texture_tiled_y(
        self, tex_id: int, x: int, y: int, w: int, h: int
    ):
        """
        Draw a texture repeated vertically to fill (w,h).
        Assumes you can resolve tex_id -> pygame.Surface, and supports scaling width.

        :param tex_id: The texture ID to draw.
        :type tex_id: int
        :param x: The x-coordinate to draw the texture.
        :type x: int
        :param y: The y-coordinate to draw the texture.
        :type y: int
        :param w: The width to draw the texture (height is determined by tiling).
        :type w: int
        :param h: The height to fill with the tiled texture.
        :type h: int
        """
