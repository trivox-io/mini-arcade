"""
Lighting render pass implementation.
"""

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade_core.backend import Backend
from mini_arcade_core.engine.render.camera import viewport_transform_for_packet
from mini_arcade_core.engine.render.context import RenderContext
from mini_arcade_core.engine.render.frame_packet import FramePacket
from mini_arcade_core.engine.render.packet import DrawOp, RenderPacket


@dataclass
class LightingPass:
    """
    Lighting Render Pass.
    This pass handles scene lighting effects.
    """

    name: str = "LightingPass"

    def run(
        self, backend: Backend, ctx: RenderContext, packets: list[FramePacket]
    ):
        """Run the lighting render pass."""
        for fp in packets:
            if fp.is_overlay:
                continue
            ops = self._layer_ops(fp.packet, "lighting")
            if ops is None or not ops:
                continue
            self._draw_ops(backend, ctx, fp.packet, ops)

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

    @staticmethod
    def _draw_ops(
        backend: Backend,
        ctx: RenderContext,
        packet: RenderPacket,
        ops: tuple[DrawOp, ...],
    ) -> None:
        ctx.stats.packets += 1
        ctx.stats.renderables += len(ops)
        ctx.stats.draw_groups += 1

        world_transform = viewport_transform_for_packet(ctx.viewport, packet)

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
            backend.set_viewport_transform(
                world_transform.ox,
                world_transform.oy,
                world_transform.s,
            )
            for op in ops:
                op(backend)
        finally:
            backend.render.clear_clip_rect()
            backend.clear_viewport_transform()
