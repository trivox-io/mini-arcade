"""
Preview scene for scene/menu_scene_base tutorial example.
"""

from __future__ import annotations

import math

from mini_arcade_core.backend.backend import Backend
from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.sim_scene import SimScene

SCENE_ID = "menu_scene_base_preview"


# Justification: This scene overrides tick directly and does not use a tick context.
# pylint: disable=abstract-method
@register_scene(SCENE_ID)
class MenuSceneBasePreviewScene(SimScene):
    """
    Lightweight target scene to validate menu navigation and commands.
    """

    def __init__(self, ctx: RuntimeContext):
        super().__init__(ctx)
        self._elapsed = 0.0
        self._frames = 0
        self._last_backend_name = "unknown"

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        self._elapsed += dt
        self._frames += 1

        level = str(self.context.settings.difficulty.level).upper()
        pulse = (math.sin(self._elapsed * 2.4) + 1.0) * 0.5
        bar_x = int(48 + pulse * 300)
        # pylint: disable=assignment-from-no-return
        vp = self.context.services.window.get_viewport()

        lines = [
            "menu_scene_base_preview",
            "",
            f"backend: {self._last_backend_name}",
            f"difficulty from menu: {level}",
            f"frame: {self._frames}",
            f"dt: {dt * 1000.0:.2f} ms",
            f"window: {vp.window_w}x{vp.window_h}",
            "",
            "Controls:",
            "  ESC back to menu",
        ]

        def draw(backend: Backend):
            self._last_backend_name = backend.__class__.__name__
            backend.render.draw_rect(22, 22, 680, 360, color=(0, 0, 0, 220))
            backend.render.draw_rect(bar_x, 300, 120, 24, color=(130, 214, 255, 255))
            y = 36
            for line in lines:
                backend.text.draw(
                    36,
                    y,
                    line,
                    color=(230, 230, 236),
                    font_size=20,
                )
                y += 24

        return RenderPacket.from_ops([draw])
