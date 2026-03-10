"""
Scene for scene/minimal_scene tutorial example.
"""

from __future__ import annotations

import math

from mini_arcade_core.backend.backend import Backend
from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.sim_scene import SimScene

SCENE_ID = "minimal_scene"


# Justification: This scene overrides tick directly and does not use a tick context.
# pylint: disable=abstract-method
@register_scene(SCENE_ID)
class MinimalScene(SimScene):
    """
    Minimal scene that renders text and one animated rectangle.
    """

    def __init__(self, ctx: RuntimeContext):
        super().__init__(ctx)
        self._elapsed = 0.0
        self._last_backend_name = "unknown"

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        del input_frame
        self._elapsed += dt

        pulse = (math.sin(self._elapsed * 2.0) + 1.0) * 0.5
        block_x = int(80 + (pulse * 320))
        block_y = 230

        lines = [
            "scene/minimal_scene",
            "",
            "Hello world.",
            "This scene only draws text and one moving rectangle.",
            "",
            f"backend: {self._last_backend_name}",
            f"entity x: {block_x}",
            "",
            "Controls:",
            "  ESC -> quit",
        ]

        def draw(backend: Backend):
            self._last_backend_name = backend.__class__.__name__
            backend.render.draw_rect(24, 24, 640, 280, color=(0, 0, 0, 220))
            backend.render.draw_rect(
                block_x, block_y, 80, 30, color=(120, 220, 255, 255)
            )
            y = 36
            for line in lines:
                backend.text.draw(
                    40,
                    y,
                    line,
                    color=(230, 230, 235),
                    font_size=18,
                )
                y += 22

        return RenderPacket.from_ops([draw])
