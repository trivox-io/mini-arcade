"""
Scene for window/fit_vs_fill tutorial example.
"""

from __future__ import annotations

from mini_arcade_core.backend.backend import Backend
from mini_arcade_core.backend.keys import Key
from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.engine.render.viewport import ViewportMode
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.sim_scene import SimScene

SCENE_ID = "fit_vs_fill"


def _visible_virtual_rect(vp) -> tuple[float, float, float, float]:
    """
    Compute visible virtual bounds for current window/viewport transform.
    """
    x0 = max(0.0, (-vp.offset_x) / vp.scale)
    y0 = max(0.0, (-vp.offset_y) / vp.scale)
    x1 = min(float(vp.virtual_w), (vp.window_w - vp.offset_x) / vp.scale)
    y1 = min(float(vp.virtual_h), (vp.window_h - vp.offset_y) / vp.scale)
    return (x0, y0, x1, y1)


# Justification: This scene overrides tick directly and does not use a tick context.
# pylint: disable=abstract-method
@register_scene(SCENE_ID)
class FitVsFillScene(SimScene):
    """
    Demonstrates FIT (letterbox) vs FILL (crop) viewport modes.
    """

    def __init__(self, ctx: RuntimeContext):
        super().__init__(ctx)
        self._last_backend_name = "unknown"

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        del dt
        services = self.context.services
        if Key.NUM_1 in input_frame.keys_pressed:
            services.window.set_viewport_mode(ViewportMode.FIT)
        if Key.NUM_2 in input_frame.keys_pressed:
            services.window.set_viewport_mode(ViewportMode.FILL)

        # pylint: disable=assignment-from-no-return
        vp = services.window.get_viewport()
        # pylint: enable=assignment-from-no-return
        vis_x0, vis_y0, vis_x1, vis_y1 = _visible_virtual_rect(vp)

        lines = [
            "window/fit_vs_fill",
            "",
            f"backend: {self._last_backend_name}",
            f"mode: {vp.mode}",
            f"virtual: {vp.virtual_w}x{vp.virtual_h}",
            f"window: {vp.window_w}x{vp.window_h}",
            f"scale: {vp.scale:.3f}",
            f"viewport rect: {vp.viewport_w}x{vp.viewport_h} @ ({vp.offset_x},{vp.offset_y})",
            (
                "visible virtual bounds: "
                f"x[{vis_x0:.1f},{vis_x1:.1f}] y[{vis_y0:.1f},{vis_y1:.1f}]"
            ),
            "",
            "FIT: entire virtual world visible, bars may appear.",
            "FILL: no bars, but virtual edges are cropped.",
            "",
            "Controls:",
            "  1 -> FIT",
            "  2 -> FILL",
            "  F1 -> debug overlay",
            "  ESC -> quit",
        ]

        def draw(backend: Backend):
            self._last_backend_name = backend.__class__.__name__

            # Background and virtual-space frame.
            backend.render.draw_rect(
                0, 0, vp.virtual_w, vp.virtual_h, color=(18, 20, 30, 255)
            )

            # Full virtual border (what exists in simulation space).
            border = (245, 210, 80, 255)
            backend.render.draw_line(0, 0, vp.virtual_w, 0, color=border)
            backend.render.draw_line(
                vp.virtual_w, 0, vp.virtual_w, vp.virtual_h, color=border
            )
            backend.render.draw_line(
                vp.virtual_w, vp.virtual_h, 0, vp.virtual_h, color=border
            )
            backend.render.draw_line(0, vp.virtual_h, 0, 0, color=border)

            # Visible virtual bounds rectangle (what actually lands inside window).
            vx = int(vis_x0)
            vy = int(vis_y0)
            vw = max(1, int(vis_x1 - vis_x0))
            vh = max(1, int(vis_y1 - vis_y0))
            backend.render.draw_rect(vx, vy, vw, vh, color=(40, 110, 170, 90))
            backend.render.draw_line(vx, vy, vx + vw, vy, color=(120, 220, 255, 255))
            backend.render.draw_line(
                vx + vw, vy, vx + vw, vy + vh, color=(120, 220, 255, 255)
            )
            backend.render.draw_line(
                vx + vw, vy + vh, vx, vy + vh, color=(120, 220, 255, 255)
            )
            backend.render.draw_line(vx, vy + vh, vx, vy, color=(120, 220, 255, 255))

            # Edge labels help visualize cropping in FILL mode.
            backend.text.draw(8, 8, "TOP", color=(255, 230, 180), font_size=18)
            backend.text.draw(
                vp.virtual_w - 66,
                8,
                "TOP-R",
                color=(255, 230, 180),
                font_size=18,
            )
            backend.text.draw(
                8,
                vp.virtual_h - 28,
                "BOTTOM-L",
                color=(255, 230, 180),
                font_size=18,
            )
            backend.text.draw(
                vp.virtual_w - 90,
                vp.virtual_h - 28,
                "BOTTOM-R",
                color=(255, 230, 180),
                font_size=18,
            )

            backend.render.draw_rect(16, 16, 760, 390, color=(0, 0, 0, 210))
            y = 28
            for line in lines:
                backend.text.draw(
                    28,
                    y,
                    line,
                    color=(230, 230, 236),
                    font_size=18,
                )
                y += 21

        return RenderPacket.from_ops([draw])
