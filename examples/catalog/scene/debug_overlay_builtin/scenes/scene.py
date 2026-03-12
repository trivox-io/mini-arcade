"""
Scene for scene/debug_overlay_builtin tutorial example.
"""

from __future__ import annotations

import math

from mini_arcade_core.backend.backend import Backend
from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.sim_scene import SimScene

SCENE_ID = "debug_overlay_builtin"
DEBUG_OVERLAY_ID = "debug_overlay"


# Justification: This scene overrides tick directly and does not use a tick context.
# pylint: disable=abstract-method
@register_scene(SCENE_ID)
class DebugOverlayBuiltinScene(SimScene):
    """
    Scene that makes built-in debug overlay behavior observable.
    """

    def __init__(self, ctx: RuntimeContext):
        super().__init__(ctx)
        self._elapsed = 0.0
        self._frames = 0
        self._overlay_active = False
        self._toggle_count = 0
        self._last_backend_name = "unknown"

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        del input_frame
        self._elapsed += dt
        self._frames += 1

        services = self.context.services
        stack = list(services.scenes.visible_entries())

        overlay_active = any(
            entry.scene_id == DEBUG_OVERLAY_ID for entry in stack
        )
        if overlay_active != self._overlay_active:
            self._overlay_active = overlay_active
            self._toggle_count += 1

        pulse = (math.sin(self._elapsed * 2.0) + 1.0) * 0.5
        bar_x = int(40 + pulse * 320)

        def draw(backend: Backend):
            self._last_backend_name = backend.__class__.__name__
            lines = [
                "scene/debug_overlay_builtin",
                "Overlay is enabled from gameplay settings.",
                "This scene contributes extra lines through debug_overlay_lines().",
                "",
                f"overlay active: {overlay_active}",
                f"overlay toggles observed: {self._toggle_count}",
                f"backend: {self._last_backend_name}",
                f"scene frames: {self._frames}",
                "",
                "F1 -> toggle built-in debug overlay",
                "ESC -> quit",
            ]
            backend.render.draw_rect(16, 16, 760, 256, color=(0, 0, 0, 220))
            backend.render.draw_rect(
                bar_x, 410, 120, 22, color=(110, 210, 255, 255)
            )
            y = 28
            for line in lines:
                backend.text.draw(
                    28,
                    y,
                    line,
                    color=(230, 230, 235),
                    font_size=18,
                )
                y += 21

        return RenderPacket.from_ops([draw])

    def debug_overlay_lines(self) -> list[str]:
        return [
            f"scene_frames: {self._frames}",
            f"overlay_toggles_observed: {self._toggle_count}",
            f"backend_hint: {self._last_backend_name}",
        ]
