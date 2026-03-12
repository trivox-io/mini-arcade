"""
Scene for window/virtual_resolution_basics tutorial example.
"""

from __future__ import annotations

import math

from mini_arcade_core.backend.backend import Backend
from mini_arcade_core.backend.keys import Key
from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.sim_scene import SimScene

SCENE_ID = "virtual_resolution_basics"
PRESETS: tuple[tuple[int, int], ...] = (
    (640, 360),
    (800, 600),
    (960, 540),
)


# Justification: This scene overrides tick directly and does not use a tick context.
# pylint: disable=abstract-method
@register_scene(SCENE_ID)
class VirtualResolutionBasicsScene(SimScene):
    """
    Demonstrates how virtual resolution affects world-space rendering.
    """

    def __init__(self, ctx: RuntimeContext):
        super().__init__(ctx)
        self._elapsed = 0.0
        self._frames = 0
        self._last_backend_name = "unknown"

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        self._elapsed += dt
        self._frames += 1

        if self.context.command_queue is not None:
            if Key.NUM_1 in input_frame.keys_pressed:
                self.context.services.window.set_virtual_resolution(
                    *PRESETS[0]
                )
            if Key.NUM_2 in input_frame.keys_pressed:
                self.context.services.window.set_virtual_resolution(
                    *PRESETS[1]
                )
            if Key.NUM_3 in input_frame.keys_pressed:
                self.context.services.window.set_virtual_resolution(
                    *PRESETS[2]
                )

        # pylint: disable=assignment-from-no-return
        vp = self.context.services.window.get_viewport()
        cfg = self.context.config
        # pylint: enable=assignment-from-no-return

        center_x = vp.virtual_w // 2
        center_y = vp.virtual_h // 2
        pulse = (math.sin(self._elapsed * 2.0) + 1.0) * 0.5
        marker_x = int(40 + pulse * max(vp.virtual_w - 80, 1))

        lines = [
            "window/virtual_resolution_basics",
            "",
            f"backend: {self._last_backend_name}",
            f"config.virtual_resolution: {cfg.virtual_resolution[0]}x{cfg.virtual_resolution[1]}",
            f"runtime virtual: {vp.virtual_w}x{vp.virtual_h}",
            f"window: {vp.window_w}x{vp.window_h}",
            f"mode: {vp.mode}",
            f"scale: {vp.scale:.3f}",
            f"viewport rect: {vp.viewport_w}x{vp.viewport_h} @ ({vp.offset_x},{vp.offset_y})",
            "",
            "Virtual world anchors (0,0), center, max edges stay meaningful.",
            "Only scale/letterboxing changes when virtual resolution changes.",
            "",
            "Controls:",
            "  1 -> virtual 640x360",
            "  2 -> virtual 800x600",
            "  3 -> virtual 960x540",
            "  ESC -> quit",
        ]

        def draw(backend: Backend):
            self._last_backend_name = backend.__class__.__name__

            # Virtual-space frame and center guides.
            backend.render.draw_rect(
                0, 0, vp.virtual_w, vp.virtual_h, color=(28, 40, 62, 255)
            )
            backend.render.draw_line(
                center_x, 0, center_x, vp.virtual_h, color=(80, 110, 160, 255)
            )
            backend.render.draw_line(
                0, center_y, vp.virtual_w, center_y, color=(80, 110, 160, 255)
            )

            # Corner markers.
            backend.render.draw_rect(0, 0, 18, 18, color=(255, 200, 80, 255))
            backend.render.draw_rect(
                vp.virtual_w - 18,
                0,
                18,
                18,
                color=(255, 200, 80, 255),
            )
            backend.render.draw_rect(
                0,
                vp.virtual_h - 18,
                18,
                18,
                color=(255, 200, 80, 255),
            )
            backend.render.draw_rect(
                vp.virtual_w - 18,
                vp.virtual_h - 18,
                18,
                18,
                color=(255, 200, 80, 255),
            )

            backend.render.draw_rect(
                marker_x,
                center_y - 10,
                30,
                20,
                color=(120, 220, 255, 255),
            )

            panel_w = min(760, max(vp.virtual_w - 40, 200))
            panel_h = min(420, max(vp.virtual_h - 40, 200))
            backend.render.draw_rect(
                20, 20, panel_w, panel_h, color=(0, 0, 0, 210)
            )
            y = 32
            for line in lines:
                backend.text.draw(
                    32,
                    y,
                    line,
                    color=(230, 230, 236),
                    font_size=18,
                )
                y += 21

        return RenderPacket.from_ops([draw])
