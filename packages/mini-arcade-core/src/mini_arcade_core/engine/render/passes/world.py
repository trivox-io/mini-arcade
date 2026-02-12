"""
World render pass implementation.
"""

from dataclasses import dataclass

from mini_arcade_core.backend import Backend
from mini_arcade_core.engine.render.context import RenderContext
from mini_arcade_core.engine.render.frame_packet import FramePacket
from mini_arcade_core.engine.render.packet import RenderPacket


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
            self._draw_packet(backend, ctx, fp.packet)

    def _draw_packet(
        self, backend: Backend, ctx: RenderContext, packet: RenderPacket
    ):
        if not packet or not packet.ops:
            return

        ctx.stats.packets += 1
        ctx.stats.renderables += len(packet.ops)
        ctx.stats.draw_groups += 1  # approx: 1 group per packet

        backend.set_viewport_transform(
            ctx.viewport.offset_x, ctx.viewport.offset_y, ctx.viewport.scale
        )
        backend.render.set_clip_rect(
            0,
            0,
            ctx.viewport.virtual_w,
            ctx.viewport.virtual_h,
        )
        try:
            for op in packet.ops:
                op(backend)
        finally:
            backend.render.clear_clip_rect()
            backend.clear_viewport_transform()
