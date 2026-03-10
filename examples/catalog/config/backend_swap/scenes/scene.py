"""
Scene for config/backend_swap tutorial example.
"""

from __future__ import annotations

from mini_arcade_core.backend.backend import Backend
from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.sim_scene import SimScene

SCENE_ID = "backend_swap"


@register_scene(SCENE_ID)
class BackendSwapScene(SimScene):
    """
    Displays runtime backend + render config for parity checks.
    """

    def __init__(self, ctx: RuntimeContext):
        super().__init__(ctx)
        self._last_backend_name = "unknown"

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        del input_frame, dt
        cfg = self.context.config
        active = ", ".join(cfg.postfx.active) if cfg.postfx.active else "(none)"

        def draw(backend: Backend):
            self._last_backend_name = backend.__class__.__name__
            lines = [
                "config/backend_swap",
                "Swap only the backend provider and keep the scene identical.",
                "",
                f"current backend: {self._last_backend_name}",
                f"virtual resolution: {cfg.virtual_resolution[0]}x{cfg.virtual_resolution[1]}",
                f"fps target: {cfg.fps}",
                f"postfx: {active}",
                "",
                "Parity checklist:",
                "  - same timing and motion",
                "  - same clear color",
                "  - same text placement",
                "",
                "ESC -> quit",
            ]
            backend.render.draw_rect(18, 18, 660, 340, color=(0, 0, 0, 0.75))
            y = 34
            for line in lines:
                backend.text.draw(20, y, line, color=(230, 230, 235), font_size=18)
                y += 22

        return RenderPacket(ops=[draw])
