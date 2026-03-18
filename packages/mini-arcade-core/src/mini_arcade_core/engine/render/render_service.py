"""
Render service definition.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from PIL import Image

from mini_arcade_core.backend.backend import Backend
from mini_arcade_core.engine.render.context import RenderStats


@dataclass
class RenderService:
    """
    Render Service.
    This service manages rendering statistics and state.
    :ivar last_frame_ms (float): Time taken for the last frame in milliseconds.
    :ivar last_stats (RenderStats): Rendering statistics from the last frame.
    """

    backend: Backend
    last_frame_ms: float = 0.0
    last_stats: RenderStats = field(default_factory=RenderStats)

    def load_texture(self, path: str) -> int:
        """
        Load a texture from a file path and return its texture ID.

        :param path: The file path to the texture image.
        :type path: str
        :return: The texture ID assigned by the backend.
        :rtype: int
        """
        img = Image.open(path).convert("RGBA")
        w, h = img.size
        data = img.tobytes()  # packed RGBA bytes
        pitch = w * 4
        # IMPORTANT: call the render port, not native backend directly
        return self.backend.render.create_texture_rgba(w, h, data, pitch)

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
        """
        self.backend.render.draw_texture_tiled_y(tex_id, x, y, w, h)
