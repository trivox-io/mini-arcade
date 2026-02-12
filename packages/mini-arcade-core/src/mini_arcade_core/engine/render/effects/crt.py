"""
CRT screen-space post effect.
"""

# Justification: PoC code for v1.
# pylint: disable=duplicate-code

from __future__ import annotations

from dataclasses import dataclass
from math import sin

from mini_arcade_core.backend import Backend
from mini_arcade_core.engine.render.context import RenderContext
from mini_arcade_core.engine.render.effects.base import EffectParams


@dataclass
class CRTEffect:
    """
    CRT screen-space post effect.
    Simulates CRT scanlines with optional wobble.
    """

    effect_id: str = "crt"

    # Justification: This is PoC code for v1.
    # pylint: disable=too-many-locals
    def apply(self, backend: Backend, ctx: RenderContext):
        """Apply the CRT effect to the current render context."""
        vp = ctx.viewport
        x0, y0 = vp.offset_x, vp.offset_y
        w, h = vp.viewport_w, vp.viewport_h

        stack = ctx.meta.get("effects_stack")
        params: EffectParams = (
            stack.params.get(self.effect_id, EffectParams())
            if stack
            else EffectParams()
        )

        intensity = max(0.0, min(1.0, params.intensity))
        if intensity <= 0.0:
            return

        # Use a time value from ctx.meta (added in Game.run below)
        t = float(ctx.meta.get("time_s", 0.0))
        wobble = float(params.wobble_speed)

        # Clip to viewport so it works with all viewport modes/resolutions
        backend.render.set_clip_rect(x0, y0, w, h)

        # Scanlines: draw every N lines with low alpha
        # Note: assumes Backend supports alpha in color tuples.
        spacing = 2  # tweakable
        base_alpha = 120  # int(40 * intensity)  # subtle
        line_color = (255, 255, 255, base_alpha)

        # "Wobble": tiny horizontal shift that animates over time
        # Keep it tiny to avoid looking like a bug.
        for y in range(y0, y0 + h, spacing):
            # shift in pixels, -2..2-ish
            shift = int(2.0 * intensity * sin((y * 0.05) + (t * wobble)))
            backend.render.draw_line(
                x0 + shift, y, x0 + w + shift, y, color=line_color
            )

        backend.render.clear_clip_rect()
