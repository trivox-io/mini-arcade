"""
UI render pass implementation.
"""

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade_core.backend import Backend
from mini_arcade_core.engine.render.context import RenderContext
from mini_arcade_core.engine.render.frame_packet import FramePacket
from mini_arcade_core.engine.render.packet import DrawOp, RenderPacket


@dataclass
class UIPass:
    """
    UI Render Pass.
    This pass handles rendering of UI overlays.
    """

    name: str = "UIPass"

    def run(
        self, backend: Backend, ctx: RenderContext, packets: list[FramePacket]
    ):
        """Run the UI render pass."""
        # UI overlays should be screen-space (no world transform / no clip).
        backend.clear_viewport_transform()
        backend.render.clear_clip_rect()

        for fp in packets:
            if fp.is_overlay:
                ops = tuple(fp.packet.ops)
            else:
                layer_ops = self._layer_ops(fp.packet, "ui")
                if layer_ops is None:
                    continue
                ops = layer_ops

            if not ops:
                continue

            ctx.stats.packets += 1
            ctx.stats.renderables += len(ops)
            ctx.stats.draw_groups += 1

            for op in ops:
                op(backend)

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
