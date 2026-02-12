"""
Pygame backend façade.
"""

from __future__ import annotations

import pygame
from mini_arcade_core.backend.viewport import ViewportTransform

from mini_arcade_pygame_backend.config import PygameBackendSettings
from mini_arcade_pygame_backend.ports.audio import AudioPort
from mini_arcade_pygame_backend.ports.capture import CapturePort
from mini_arcade_pygame_backend.ports.input import InputPort
from mini_arcade_pygame_backend.ports.render import RenderPort
from mini_arcade_pygame_backend.ports.text import TextPort
from mini_arcade_pygame_backend.ports.window import WindowPort


# Justification: Many instance attributes for ports
# pylint: disable=too-many-instance-attributes
class PygameBackend:
    """
    Pygame backend for mini-arcade.

    :ivar settings: Backend settings.
    """

    def __init__(self, settings: PygameBackendSettings) -> None:
        """
        Initialize the PygameBackend with the given settings.

        :param settings: Backend settings.
        :type settings: PygameBackendSettings
        """
        self._settings = settings or PygameBackendSettings()
        self._vp = ViewportTransform()

        # Ports (created after init)
        self.window: WindowPort | None = None
        self.input: InputPort | None = None
        self.render: RenderPort | None = None
        self.text: TextPort | None = None
        self.audio: AudioPort | None = None
        self.capture: CapturePort | None = None

        self._initialized = False

    def init(self):
        """
        Initialize the pygame backend.
        This method sets up the necessary components for the backend to function.
        """
        # 1) pygame init
        pygame.init()
        pygame.font.init()

        # 2) create screen surface, clock, etc.

        # 3) build ports, passing runtime objects + settings + vp
        ws = self._settings.core.window
        rs = self._settings.core.renderer
        fonts = self._settings.core.fonts
        aud = self._settings.core.audio

        self.window = WindowPort(
            width=ws.width,
            height=ws.height,
            title=ws.title,
            resizable=ws.resizable,
        )

        self.input = InputPort()
        self.render = RenderPort(
            self.window, self._vp, background_color=rs.background_color
        )

        font_path = fonts[0].path if fonts and fonts[0].path else None
        self.text = TextPort(
            self.window,
            self._vp,
            font_path=str(font_path) if font_path else None,
        )

        self.audio = AudioPort()
        if aud.enable:
            self.audio.init()
            if aud.sounds:
                for sid, p in aud.sounds.items():
                    self.audio.load_sound(sid, p)

        self.capture = CapturePort(self.window)
        self._initialized = True

    # ---- viewport transform (core expects these) ----
    def set_viewport_transform(
        self, offset_x: int, offset_y: int, scale: float
    ):
        """
        Set the viewport transform.

        :param offset_x: The x offset.
        :type offset_x: int
        :param offset_y: The y offset.
        :type offset_y: int
        :param scale: The scale factor.
        :type scale: float
        """
        self._vp.ox = int(offset_x)
        self._vp.oy = int(offset_y)
        self._vp.s = float(scale)

    def clear_viewport_transform(self):
        """Clear the viewport transform (reset to defaults)."""
        self._vp.ox = 0
        self._vp.oy = 0
        self._vp.s = 1.0
