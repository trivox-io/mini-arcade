"""
Scene for config/engine_config_basics tutorial example.
"""

from __future__ import annotations

from mini_arcade_core.backend.backend import Backend
from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.sim_scene import SimScene


# Justification: This scene overrides tick directly and doesn't need tick context.
# pylint: disable=abstract-method
@register_scene("engine_config_basics")
class EngineConfigBasicsScene(SimScene):
    """
    Shows effective engine configuration at runtime.
    """

    def __init__(self, ctx: RuntimeContext):
        super().__init__(ctx)
        self._last_backend_name = "unknown"

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        cfg = self.context.config
        vp = self.context.services.window.get_viewport()
        active = ", ".join(cfg.postfx.active) if cfg.postfx.active else "(none)"

        lines = [
            "config/engine_config_basics",
            "",
            f"backend: {self._last_backend_name}",
            f"initial_scene: {cfg.initial_scene}",
            f"fps target: {cfg.fps}",
            f"virtual_resolution: {cfg.virtual_resolution[0]}x{cfg.virtual_resolution[1]}",
            f"postfx.enabled: {cfg.postfx.enabled}",
            f"postfx.active: {active}",
            f"enable_profiler: {cfg.enable_profiler}",
            "",
            f"window: {vp.window_w}x{vp.window_h}",
            f"viewport mode: {vp.mode}",
            f"viewport scale: {vp.scale:.3f}",
            "",
            "Controls:",
            "  F1 toggle debug overlay",
            "  ESC exit",
        ]

        def draw(backend: Backend):
            self._last_backend_name = backend.__class__.__name__
            backend.render.draw_rect(12, 12, 620, 410, color=(0, 0, 0, 0.75))
            y = 24
            for line in lines:
                backend.text.draw(20, y, line, color=(230, 230, 235), font_size=18)
                y += 22

        return RenderPacket(ops=[draw])

