"""
Vignette noise screen-space post effect.
"""

# Justification: PoC code for v1.
# pylint: disable=duplicate-code

from __future__ import annotations

import random
from dataclasses import dataclass

from mini_arcade_core.backend import Backend
from mini_arcade_core.engine.render.context import RenderContext
from mini_arcade_core.engine.render.effects.base import EffectParams


@dataclass
class VignetteNoiseEffect:
    """
    Vignette + noise screen-space post effect.
    Simulates a vignette effect with added noise/grain.
    """

    effect_id: str = "vignette_noise"

    # Justification: This is PoC code for v1.
    # pylint: disable=too-many-locals
    def apply(self, backend: Backend, ctx: RenderContext):
        """Apply the Vignette + Noise effect to the current render context."""
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

        backend.render.set_clip_rect(x0, y0, w, h)

        # Vignette approximation: draw edge rectangles with increasing alpha.
        # Not a true radial gradient, but good enough for v1.
        steps = 10
        max_alpha = int(110 * intensity)  # subtle
        for i in range(steps):
            # thickness grows inward
            t = i + 1
            alpha = int(max_alpha * (t / steps))
            color = (0, 0, 0, alpha)

            # top
            backend.render.draw_rect(x0, y0, w, t, color=color)
            # bottom
            backend.render.draw_rect(x0, y0 + h - t, w, t, color=color)
            # left
            backend.render.draw_rect(x0, y0, t, h, color=color)
            # right
            backend.render.draw_rect(x0 + w - t, y0, t, h, color=color)

        # Noise: sprinkle a few pixels (or tiny 1x1 rects).
        # Use deterministic-ish seed per frame so it doesn't “swim” too much.
        frame = int(ctx.meta.get("frame_index", 0))
        random.seed(frame * 1337)

        dots = int(200 * intensity)  # tweak
        for _ in range(dots):
            px = x0 + random.randint(0, max(0, w - 1))
            py = y0 + random.randint(0, max(0, h - 1))
            a = random.randint(10, int(50 * intensity) + 10)
            backend.render.draw_rect(px, py, 1, 1, color=(255, 255, 255, a))

        backend.render.clear_clip_rect()
