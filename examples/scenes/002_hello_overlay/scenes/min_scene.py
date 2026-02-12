"""
Minimal scene example with Debug Overlay (systems + draw_ops).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from mini_arcade.utils.logging import logger  # type: ignore[import-not-found]
from mini_arcade_core.backend.backend import (
    Backend,  # type: ignore[import-not-found]
)
from mini_arcade_core.backend.keys import Key  # type: ignore[import-not-found]
from mini_arcade_core.runtime.context import (
    RuntimeContext,  # type: ignore[import-not-found]
)
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.autoreg import (
    register_scene,  # type: ignore[import-not-found]
)
from mini_arcade_core.scenes.sim_scene import (  # type: ignore[import-not-found]
    BaseIntent,
    BaseTickContext,
    BaseWorld,
    Drawable,
    DrawCall,
    SimScene,
)
from mini_arcade_core.scenes.systems.builtins import (  # type: ignore[import-not-found]
    BaseInputSystem,
    BaseRenderSystem,
)
from mini_arcade_core.scenes.systems.system_pipeline import SystemPipeline


# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------
def _ema(prev: float, cur: float, alpha: float = 0.15) -> float:
    """Exponential moving average for stable display."""
    return cur if prev <= 0.0 else (prev * (1.0 - alpha) + cur * alpha)


# --------------------------------------------------------------------------------------
# World / Intent / Tick context
# --------------------------------------------------------------------------------------
@dataclass
class DebugOverlayState:
    enabled: bool = True
    fps_smoothed: float = 0.0
    frame_ms_smoothed: float = 0.0


@dataclass
class MinWorld(BaseWorld):
    """Minimal world state for our example scene."""

    overlay: DebugOverlayState = field(default_factory=DebugOverlayState)


@dataclass(frozen=True)
class MinIntent(BaseIntent):
    """Minimal intent for our example scene."""

    toggle_overlay: bool = False


@dataclass
class MinTickContext(BaseTickContext[MinWorld, MinIntent]):
    """Context for a Min scene tick."""


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
class MinInputSystem(BaseInputSystem):
    """Reads input and sets intent."""

    name: str = "min_input"
    order: int = 10

    def step(self, ctx: MinTickContext):
        pressed = ctx.input_frame.keys_pressed
        ctx.intent = MinIntent(toggle_overlay=Key.F1 in pressed)


@dataclass
class DebugOverlaySystem:
    """
    Updates overlay state (toggle + perf stats).
    """

    name: str = "debug_overlay"
    order: int = 20  # after input

    def step(self, ctx: MinTickContext):
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
            ov.fps_smoothed = _ema(ov.fps_smoothed, fps)
            ov.frame_ms_smoothed = _ema(ov.frame_ms_smoothed, frame_ms)


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
        self.world = MinWorld()
        self.systems.extend(
            [MinInputSystem(), DebugOverlaySystem(), MinRenderSystem()]
        )
