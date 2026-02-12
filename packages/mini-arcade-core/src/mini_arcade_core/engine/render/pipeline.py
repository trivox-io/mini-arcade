"""
Render pipeline module.
Defines the RenderPipeline class for rendering RenderPackets.
"""

# Justification: This code is duplicated in multiple places for clarity and separation
# of concerns.
# try:
#     for op in packet.ops:
#         op(backend)
# finally:
#     backend.clear_clip_rect()
#     backend.clear_viewport_transform() (duplicate-code)
# pylint: disable=duplicate-code

from __future__ import annotations

from dataclasses import dataclass, field

from mini_arcade_core.backend import Backend
from mini_arcade_core.engine.render.context import RenderContext
from mini_arcade_core.engine.render.frame_packet import FramePacket
from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.engine.render.passes.base import RenderPass
from mini_arcade_core.engine.render.passes.begin_frame import BeginFramePass
from mini_arcade_core.engine.render.passes.end_frame import EndFramePass
from mini_arcade_core.engine.render.passes.lighting import LightingPass
from mini_arcade_core.engine.render.passes.postfx import PostFXPass
from mini_arcade_core.engine.render.passes.ui import UIPass
from mini_arcade_core.engine.render.passes.world import WorldPass
from mini_arcade_core.engine.render.viewport import ViewportState


@dataclass
class RenderPipeline:
    """
    Minimal pipeline for v1.

    Later you can expand this into passes:
        - build draw list
        - cull
        - sort
        - backend draw pass

    :cvar passes: list[RenderPass]: List of render passes to execute in order.
    """

    passes: list[RenderPass] = field(
        default_factory=lambda: [
            BeginFramePass(),
            WorldPass(),
            LightingPass(),
            UIPass(),
            PostFXPass(),
            EndFramePass(),
        ]
    )

    def render_frame(
        self, backend: Backend, ctx: RenderContext, packets: list[FramePacket]
    ):
        """
        Render a frame using the provided Backend, RenderContext, and list of FramePackets.

        :param backend: Backend to use for rendering.
        :type backend: Backend

        :param ctx: RenderContext containing rendering state.
        :type ctx: RenderContext

        :param packets: List of FramePackets to render.
        :type packets: list[FramePacket]
        """
        for p in self.passes:
            p.run(backend, ctx, packets)

    def draw_packet(
        self,
        backend: Backend,
        packet: RenderPacket,
        viewport_state: ViewportState,
    ):
        """
        Draw the given RenderPacket using the provided Backend.

        :param backend: Backend to use for drawing.
        :type backend: Backend

        :param packet: RenderPacket to draw.
        :type packet: RenderPacket
        """
        if not packet:
            return

        backend.set_viewport_transform(
            viewport_state.offset_x,
            viewport_state.offset_y,
            viewport_state.scale,
        )

        backend.set_clip_rect(
            0,
            0,
            viewport_state.viewport_w,
            viewport_state.viewport_h,
        )

        try:
            for op in packet.ops:
                op(backend)
        finally:
            backend.clear_clip_rect()
            backend.clear_viewport_transform()
