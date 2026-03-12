"""
Scene for window/resize_reflow tutorial example.
"""

from __future__ import annotations

import math

from mini_arcade_core.backend.backend import Backend
from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.sim_scene import SimScene

from examples._shared.text_layout import draw_text_block, fit_text_block

SCENE_ID = "resize_reflow"


def _clamp(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))


# Justification: This scene overrides tick directly and does not use a tick context.
# pylint: disable=abstract-method
@register_scene(SCENE_ID)
class ResizeReflowScene(SimScene):
    """
    Demonstrates dynamic UI reflow driven by window resize.
    """

    def __init__(self, ctx: RuntimeContext):
        super().__init__(ctx)
        self._elapsed = 0.0
        self._last_backend_name = "unknown"
        self._last_window = (0, 0)
        self._resize_count = 0

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        del input_frame
        self._elapsed += dt

        # pylint: disable=assignment-from-no-return
        vp = self.context.services.window.get_viewport()
        # pylint: enable=assignment-from-no-return
        current_window = (vp.window_w, vp.window_h)
        if current_window != self._last_window:
            if self._last_window != (0, 0):
                self._resize_count += 1
            self._last_window = current_window

        pulse = (math.sin(self._elapsed * 2.1) + 1.0) * 0.5
        world_marker_x = int(40 + pulse * max(vp.virtual_w - 80, 1))

        # UI layout recomputed every frame from current window size.
        panel_w = _clamp(int(vp.window_w * 0.36), 280, 460)
        panel_h = _clamp(int(vp.window_h * 0.52), 220, 380)
        panel_x = vp.window_w - panel_w - 20
        panel_y = 20

        footer_h = 46
        footer_x = 18
        footer_y = vp.window_h - footer_h - 14
        footer_w = max(220, vp.window_w - 36)

        ui_lines = [
            "window/resize_reflow",
            "",
            f"backend: {self._last_backend_name}",
            f"window: {vp.window_w}x{vp.window_h}",
            f"virtual: {vp.virtual_w}x{vp.virtual_h}",
            f"mode: {vp.mode}",
            f"scale: {vp.scale:.3f}",
            f"resize count: {self._resize_count}",
            "",
            "UI panel is anchored to top-right in screen-space.",
            "Footer is anchored to bottom in screen-space.",
            "Both recompute layout from current window size each tick.",
            "",
            "Controls:",
            "  Resize window to observe reflow",
            "  ESC -> quit",
        ]

        def draw_world(backend: Backend):
            self._last_backend_name = backend.__class__.__name__
            backend.render.draw_rect(
                0, 0, vp.virtual_w, vp.virtual_h, color=(12, 18, 34, 255)
            )
            center_y = vp.virtual_h // 2
            backend.render.draw_line(
                0, center_y, vp.virtual_w, center_y, color=(76, 98, 150, 255)
            )
            backend.render.draw_rect(
                world_marker_x,
                center_y - 16,
                32,
                32,
                color=(120, 215, 255, 255),
            )

        def draw_ui(backend: Backend):
            # Screen-space UI (UIPass): no viewport transform.
            panel_pad_x = 14
            panel_pad_y = 12
            panel_layout = fit_text_block(
                backend,
                ui_lines,
                max_width=panel_w - (panel_pad_x * 2),
                max_height=panel_h - (panel_pad_y * 2),
                preferred_font_size=17,
                min_font_size=8,
            )
            footer_text = "Panel follows width. Footer follows the window."
            footer_layout = fit_text_block(
                backend,
                [footer_text],
                max_width=footer_w - 28,
                max_height=footer_h - 16,
                preferred_font_size=16,
                min_font_size=8,
            )
            backend.render.draw_rect(
                panel_x, panel_y, panel_w, panel_h, color=(0, 0, 0, 215)
            )
            draw_text_block(
                backend,
                x=panel_x + panel_pad_x,
                y=panel_y + panel_pad_y,
                lines=ui_lines,
                layout=panel_layout,
                color=(232, 232, 236),
            )

            backend.render.draw_rect(
                footer_x, footer_y, footer_w, footer_h, color=(20, 30, 56, 230)
            )
            draw_text_block(
                backend,
                x=footer_x + 14,
                y=footer_y
                + max(4, (footer_h - footer_layout.total_height) // 2),
                lines=[footer_text],
                layout=footer_layout,
                color=(220, 228, 240),
            )

        return RenderPacket.from_ops(
            [],
            pass_ops={
                "world": [draw_world],
                "ui": [draw_ui],
            },
        )
