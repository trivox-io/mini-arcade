"""
Post-processing effects render pass implementation.
"""

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade_core.backend import Backend
from mini_arcade_core.engine.render.context import RenderContext
from mini_arcade_core.engine.render.effects.registry import EffectRegistry
from mini_arcade_core.engine.render.frame_packet import FramePacket
from mini_arcade_core.engine.render.packet import DrawOp, RenderPacket


@dataclass
class PostFXPass:
    """
    PostFX Render Pass.
    This pass handles scene effect-layer draw ops and optional post-processing.
    """

    name: str = "PostFXPass"
    registry: EffectRegistry | None = None

    def run(
        self, backend: Backend, ctx: RenderContext, packets: list[FramePacket]
    ):
        """Run the post-processing effects render pass."""
        self._draw_effect_layer(backend, ctx, packets)
        self._apply_screen_effects(backend, ctx)

    def _draw_effect_layer(
        self, backend: Backend, ctx: RenderContext, packets: list[FramePacket]
    ) -> None:
        for fp in packets:
            if fp.is_overlay:
                continue
            ops = self._layer_ops(fp.packet, "effects")
            if ops is None or not ops:
                continue

            ctx.stats.packets += 1
            ctx.stats.renderables += len(ops)
            ctx.stats.draw_groups += 1

            backend.set_viewport_transform(
                ctx.viewport.offset_x,
                ctx.viewport.offset_y,
                ctx.viewport.scale,
            )
            backend.render.set_clip_rect(
                0,
                0,
                ctx.viewport.virtual_w,
                ctx.viewport.virtual_h,
            )
            try:
                for op in ops:
                    op(backend)
            finally:
                backend.render.clear_clip_rect()
                backend.clear_viewport_transform()

    def _apply_screen_effects(
        self, backend: Backend, ctx: RenderContext
    ) -> None:
        stack = ctx.meta.get("effects_stack")
        if stack is None or not stack.is_active():
            return

        # Screen space: no transforms
        backend.clear_viewport_transform()
        backend.render.clear_clip_rect()

        reg = self.registry
        if reg is None:
            return

        for effect_id in list(stack.active):
            effect = reg.get(effect_id)
            if effect is None:
                continue
            effect.apply(backend, ctx)

    @staticmethod
    def _layer_ops(
        packet: RenderPacket, key: str
    ) -> tuple[DrawOp, ...] | None:
        raw = packet.meta.get("pass_ops")
        if not isinstance(raw, dict):
            return None
        ops = raw.get(key)
        if ops is None:
            return tuple()
        return tuple(ops)
