"""
World render pass implementation.
"""

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade_core.backend import Backend
from mini_arcade_core.engine.render.camera import viewport_transform_for_packet
from mini_arcade_core.engine.render.context import RenderContext
from mini_arcade_core.engine.render.frame_packet import FramePacket
from mini_arcade_core.engine.render.packet import DrawOp, RenderPacket


@dataclass
class WorldPass:
    """
    World Render Pass.
    This pass handles rendering of world-space objects.
    """

    name: str = "WorldPass"

    def run(
        self, backend: Backend, ctx: RenderContext, packets: list[FramePacket]
    ):
        """Run the world render pass."""
        for fp in packets:
            if fp.is_overlay:
                continue
            layer_ops = self._layer_ops(fp.packet, "world")
            if layer_ops is not None:
                self._draw_ops(backend, ctx, fp.packet, layer_ops)
                continue
            self._draw_packet(backend, ctx, fp.packet)

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

    def _draw_packet(
        self, backend: Backend, ctx: RenderContext, packet: RenderPacket
    ):
        if not packet or not packet.ops:
            return
        self._draw_ops(backend, ctx, packet, packet.ops)

    def _draw_ops(
        self,
        backend: Backend,
        ctx: RenderContext,
        packet: RenderPacket,
        ops: tuple[DrawOp, ...],
    ):
        if not ops:
            return

        ctx.stats.packets += 1
        ctx.stats.renderables += len(ops)
        ctx.stats.draw_groups += 1  # approx: 1 group per packet
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
