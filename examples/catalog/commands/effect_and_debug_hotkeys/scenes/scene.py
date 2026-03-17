"""
Effect and debug hotkeys demo scene.

Binds function keys and letter keys to toggle visual effects and
debug overlays.  A status panel shows each toggle state.

  F1 → toggle bounding boxes
  F2 → toggle grid overlay
  F3 → toggle FPS display
  B  → cycle background color
"""

from __future__ import annotations

from mini_arcade_core.backend import Backend
from mini_arcade_core.backend.keys import Key
from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.sim_scene import SimScene

SCENE_ID = "hotkeys_demo"

_PANEL = (0, 0, 0, 200)
_LABEL = (140, 180, 255)
_VAL = (255, 255, 255)
_ON = (100, 255, 100)
_OFF = (255, 80, 80)

_BG_COLORS = [
    (16, 18, 28),
    (40, 10, 10),
    (10, 40, 10),
    (10, 10, 40),
    (40, 40, 10),
]


@register_scene(SCENE_ID)
class HotkeysDemoScene(SimScene):
    """Toggle debug/effect overlays with hotkeys."""

    def __init__(self, ctx: RuntimeContext):
        super().__init__(ctx)
        self._show_bounds = False
        self._show_grid = False
        self._show_fps = False
        self._bg_index = 0
        self._frame_count = 0
        self._fps_accum = 0.0
        self._fps_display = 0.0

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        # Toggle hotkeys
        if Key.F1 in input_frame.keys_pressed:
            self._show_bounds = not self._show_bounds
        if Key.F2 in input_frame.keys_pressed:
            self._show_grid = not self._show_grid
        if Key.F3 in input_frame.keys_pressed:
            self._show_fps = not self._show_fps
        if Key.B in input_frame.keys_pressed:
            self._bg_index = (self._bg_index + 1) % len(_BG_COLORS)

        # FPS counter
        self._frame_count += 1
        self._fps_accum += dt
        if self._fps_accum >= 0.5:
            self._fps_display = self._frame_count / self._fps_accum
            self._frame_count = 0
            self._fps_accum = 0.0

        show_bounds = self._show_bounds
        show_grid = self._show_grid
        show_fps = self._show_fps
        bg = _BG_COLORS[self._bg_index]
        fps_val = self._fps_display

        def draw(backend: Backend):
            r = backend.render
            t = backend.text

            # Background fill
            r.draw_rect(0, 0, 800, 600, color=bg)

            # Grid overlay
            if show_grid:
                grid_col = (60, 60, 60, 120)
                for gx in range(0, 800, 40):
                    r.draw_line(gx, 0, gx, 600, color=grid_col)
                for gy in range(0, 600, 40):
                    r.draw_line(0, gy, 800, gy, color=grid_col)

            # Fake entities for bounding-box demo
            boxes = [
                (100, 200, 80, 60, (200, 100, 100)),
                (300, 150, 50, 50, (100, 200, 100)),
                (500, 350, 120, 40, (100, 100, 200)),
            ]
            for bx, by, bw, bh, col in boxes:
                r.draw_rect(bx, by, bw, bh, color=col)
                if show_bounds:
                    r.draw_line(bx, by, bx + bw, by, color=(255, 255, 0))
                    r.draw_line(
                        bx + bw, by, bx + bw, by + bh, color=(255, 255, 0)
                    )
                    r.draw_line(
                        bx + bw, by + bh, bx, by + bh, color=(255, 255, 0)
                    )
                    r.draw_line(bx, by + bh, bx, by, color=(255, 255, 0))

            # Status panel
            r.draw_rect(16, 16, 320, 200, color=_PANEL)
            y = 28
            t.draw(24, y, "Effect & Debug Hotkeys", color=_LABEL)
            y += 28

            toggles = [
                ("F1  Bounding boxes", show_bounds),
                ("F2  Grid overlay", show_grid),
                ("F3  FPS display", show_fps),
            ]
            for label, active in toggles:
                col = _ON if active else _OFF
                state = "ON" if active else "OFF"
                t.draw(24, y, f"{label}: {state}", color=col)
                y += 22

            t.draw(24, y, f"B   Background: {bg}", color=_VAL)
            y += 28

            # FPS overlay
            if show_fps:
                r.draw_rect(680, 16, 110, 24, color=_PANEL)
                t.draw(688, 18, f"FPS: {fps_val:.0f}", color=_ON)

        return RenderPacket.from_ops([draw])
