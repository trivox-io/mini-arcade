"""
Scene for window/screen_to_virtual_input tutorial example.
"""

from __future__ import annotations


# isort owns import ordering; pylint misclassifies local packages as third-party.
# pylint: disable=wrong-import-order
from examples._shared.text_layout import draw_text_block, fit_text_block
from mini_arcade_core.backend.backend import Backend
from mini_arcade_core.backend.keys import Key
from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.engine.render.viewport import ViewportMode
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.sim_scene import SimScene

SCENE_ID = "screen_to_virtual_input"
MAX_TRAIL = 120


def _clamp(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))


# Justification: This scene overrides tick directly and does not use a tick context.
# pylint: disable=abstract-method
@register_scene(SCENE_ID)
class ScreenToVirtualInputScene(SimScene):
    """
    Demonstrates mapping mouse screen coordinates into virtual coordinates.
    """

    def __init__(self, ctx: RuntimeContext):
        super().__init__(ctx)
        self._trail: list[tuple[float, float]] = []
        self._last_backend_name = "unknown"

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        del dt
        services = self.context.services
        if Key.NUM_1 in input_frame.keys_pressed:
            services.window.set_viewport_mode(ViewportMode.FIT)
        if Key.NUM_2 in input_frame.keys_pressed:
            services.window.set_viewport_mode(ViewportMode.FILL)
        if Key.C in input_frame.keys_pressed:
            self._trail.clear()

        screen_x, screen_y = input_frame.mouse_pos
        # pylint: disable=assignment-from-no-return
        virtual_x, virtual_y = services.window.screen_to_virtual(
            float(screen_x), float(screen_y)
        )

        if input_frame.mouse_delta != (0, 0):
            self._trail.append((virtual_x, virtual_y))
            if len(self._trail) > MAX_TRAIL:
                self._trail = self._trail[-MAX_TRAIL:]

        # pylint: disable=assignment-from-no-return
        vp = services.window.get_viewport()
        # pylint: enable=assignment-from-no-return
        inside_virtual = 0.0 <= virtual_x <= float(
            vp.virtual_w
        ) and 0.0 <= virtual_y <= float(vp.virtual_h)

        panel_lines = [
            "window/screen_to_virtual_input",
            "",
            f"backend: {self._last_backend_name}",
            f"mode: {vp.mode}",
            f"window: {vp.window_w}x{vp.window_h}",
            f"virtual: {vp.virtual_w}x{vp.virtual_h}",
            f"scale: {vp.scale:.3f}",
            f"offset: ({vp.offset_x},{vp.offset_y})",
            "",
            f"screen mouse: ({screen_x},{screen_y})",
            f"virtual mouse: ({virtual_x:.2f},{virtual_y:.2f})",
            f"inside virtual bounds: {inside_virtual}",
            f"mouse delta: {input_frame.mouse_delta}",
            "",
            "Controls:",
            "  Move mouse to update mapping",
            "  1 -> FIT mode",
            "  2 -> FILL mode",
            "  C -> clear virtual trail",
            "  ESC -> quit",
        ]

        def draw_world(backend: Backend):
            self._last_backend_name = backend.__class__.__name__
            backend.render.draw_rect(
                0, 0, vp.virtual_w, vp.virtual_h, color=(16, 18, 30, 255)
            )

            # Virtual border
            border = (255, 214, 100, 255)
            backend.render.draw_line(0, 0, vp.virtual_w, 0, color=border)
            backend.render.draw_line(
                vp.virtual_w, 0, vp.virtual_w, vp.virtual_h, color=border
            )
            backend.render.draw_line(
                vp.virtual_w, vp.virtual_h, 0, vp.virtual_h, color=border
            )
            backend.render.draw_line(0, vp.virtual_h, 0, 0, color=border)

            # Trail in virtual space
            if len(self._trail) >= 2:
                for idx in range(1, len(self._trail)):
                    a = self._trail[idx - 1]
                    b = self._trail[idx]
                    backend.render.draw_line(
                        int(a[0]),
                        int(a[1]),
                        int(b[0]),
                        int(b[1]),
                        color=(120, 220, 255, 255),
                    )

            backend.render.draw_circle(
                int(virtual_x),
                int(virtual_y),
                10,
                color=(255, 140, 120, 255),
            )

        def draw_ui(backend: Backend):
            # Crosshair in screen-space (raw mouse coordinates).
            backend.render.draw_line(
                int(screen_x) - 12,
                int(screen_y),
                int(screen_x) + 12,
                int(screen_y),
                color=(255, 255, 255, 255),
            )
            backend.render.draw_line(
                int(screen_x),
                int(screen_y) - 12,
                int(screen_x),
                int(screen_y) + 12,
                color=(255, 255, 255, 255),
            )

            panel_w = _clamp(int(vp.window_w * 0.42), 420, 520)
            panel_h = _clamp(int(vp.window_h * 0.72), 320, 460)
            panel_pad_x = 12
            panel_pad_y = 12
            panel_layout = fit_text_block(
                backend,
                panel_lines,
                max_width=panel_w - (panel_pad_x * 2),
                max_height=panel_h - (panel_pad_y * 2),
                preferred_font_size=17,
                min_font_size=8,
            )

            backend.render.draw_rect(
                16, 16, panel_w, panel_h, color=(0, 0, 0, 220)
            )
            draw_text_block(
                backend,
                x=16 + panel_pad_x,
                y=16 + panel_pad_y,
                lines=panel_lines,
                layout=panel_layout,
                color=(230, 230, 236),
            )

        return RenderPacket.from_ops(
            [],
            pass_ops={
                "world": [draw_world],
                "ui": [draw_ui],
            },
        )
