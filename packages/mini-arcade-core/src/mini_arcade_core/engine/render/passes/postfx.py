"""
Post-processing effects render pass implementation.
"""

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade_core.backend import Backend
from mini_arcade_core.engine.render.context import RenderContext
from mini_arcade_core.engine.render.effects.registry import EffectRegistry
from mini_arcade_core.engine.render.frame_packet import FramePacket


@dataclass
class PostFXPass:
    """
    PostFX Render Pass.
    This pass handles post-processing effects like CRT simulation.
    """

    name: str = "PostFXPass"
    registry: EffectRegistry | None = None

    # Justification: No implementation yet
    # pylint: disable=unused-argument
    def run(
        self, backend: Backend, ctx: RenderContext, packets: list[FramePacket]
    ):
        """Run the post-processing effects render pass."""
        # Zero overhead path (no effects configured)
        stack = ctx.meta.get("effects_stack")
        if stack is None or not stack.is_active():
            return

        # Screen space: no transforms
        backend.clear_viewport_transform()
        backend.render.clear_clip_rect()

        reg = self.registry
        if reg is None:
            # no registry => nothing to do
            return

        for effect_id in list(stack.active):
            effect = reg.get(effect_id)
            if effect is None:
                continue
            effect.apply(backend, ctx)
