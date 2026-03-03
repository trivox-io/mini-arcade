"""
Minimal scene example with Debug Overlay (systems + draw_ops).
"""

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade.utils.logging import logger  # type: ignore[import-not-found]
from mini_arcade_core.backend.backend import (
    Backend,  # type: ignore[import-not-found]
)
from mini_arcade_core.backend.keys import Key  # type: ignore[import-not-found]
from mini_arcade_core.scenes.autoreg import (
    register_scene,  # type: ignore[import-not-found]
)
from mini_arcade_core.scenes.sim_scene import (  # type: ignore[import-not-found]
    Drawable,
    DrawCall,
    SimScene,
)
from mini_arcade_core.scenes.systems.builtins import (  # type: ignore[import-not-found]
    BaseRenderSystem,
    InputIntentSystem,
)

from .models import MinIntent, MinTickContext, MinWorld


# --------------------------------------------------------------------------------------
# Drawables
# --------------------------------------------------------------------------------------
class DrawDebugOverlay(Drawable[MinTickContext]):
    """Drawable for the debug overlay."""

    def __init__(self, scene_label: str = "min"):
        self.scene_label = scene_label

    def draw(self, backend: Backend, ctx: MinTickContext):
        ov = ctx.world.overlay
        if not ov.enabled:
            return

        backend_name = backend.__class__.__name__

        lines = [
            f"Scene: {self.scene_label}",
            f"Backend: {backend_name}",
            f"FPS: {ov.fps_smoothed:0.1f}",
            f"Frame: {ov.frame_ms_smoothed:0.2f} ms",
            "F1: toggle overlay",
        ]

        x, y = 10, 10
        for i, line in enumerate(lines):
            backend.text.draw(x, y + i * 18, line, color=(200, 200, 200))


# --------------------------------------------------------------------------------------
# Systems
# --------------------------------------------------------------------------------------
@dataclass
class MinInputSystem(InputIntentSystem):
    """Reads input and sets intent."""

    name: str = "min_input"
    order: int = 10

    def build_intent(self, ctx: MinTickContext):
        pressed = ctx.input_frame.keys_pressed
        ctx.intent = MinIntent(toggle_overlay=Key.F1 in pressed)


@dataclass
class DebugOverlaySystem:
    """
    Updates overlay state (toggle + perf stats).
    """

    name: str = "debug_overlay"
    order: int = 20  # after input

    @staticmethod
    def _ema(prev: float, cur: float, alpha: float = 0.15) -> float:
        """Exponential moving average for stable display."""
        return cur if prev <= 0.0 else (prev * (1.0 - alpha) + cur * alpha)

    def step(self, ctx: MinTickContext):
        """
        Update overlay state:

        :param ctx: the tick context
        :type ctx: MinTickContext
        """
        ov = ctx.world.overlay

        # toggle (edge-triggered by keys_pressed via intent)
        if ctx.intent and ctx.intent.toggle_overlay:
            ov.enabled = not ov.enabled
            logger.info("Overlay: %s", "ON" if ov.enabled else "OFF")

        # update stats (even if disabled is OK, but we can skip)
        if not ov.enabled:
            return

        if ctx.dt > 0.0:
            fps = 1.0 / ctx.dt
            frame_ms = ctx.dt * 1000.0
            ov.fps_smoothed = self._ema(ov.fps_smoothed, fps)
            ov.frame_ms_smoothed = self._ema(ov.frame_ms_smoothed, frame_ms)


@dataclass
class MinRenderSystem(BaseRenderSystem):
    """Build draw_ops (world pass empty + overlay as UI pass)."""

    name: str = "min_render"
    order: int = 100

    def step(self, ctx: MinTickContext):
        # World pass (none for this minimal scene)
        ops = []

        # UI pass: overlay last
        if ctx.world.overlay.enabled:
            ops.append(
                DrawCall(drawable=DrawDebugOverlay(scene_label="min"), ctx=ctx)
            )

        ctx.draw_ops = ops
        super().step(ctx)


# --------------------------------------------------------------------------------------
# Scene
# --------------------------------------------------------------------------------------
@register_scene("min")
class MinScene(SimScene[MinTickContext, MinWorld]):
    """
    Minimal scene that draws a debug overlay (scene name, backend name, FPS/frame time).
    """

    tick_context_type = MinTickContext

    def on_enter(self) -> None:
        self.world = MinWorld(entities=[])
        self.systems.extend(
            [MinInputSystem(), DebugOverlaySystem(), MinRenderSystem()]
        )
