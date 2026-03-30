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
from mini_arcade_core.engine.render.camera import viewport_transform_for_packet
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
        self.render_frame_content(backend, ctx, packets)
        self.present_frame(backend, ctx)

    def render_frame_content(
        self, backend: Backend, ctx: RenderContext, packets: list[FramePacket]
    ) -> None:
        """Render the frame contents without presenting them yet."""
        for p in self.passes:
            if isinstance(p, EndFramePass):
                continue
            p.run(backend, ctx, packets)

    def render_presentation_overlays(
        self, backend: Backend, ctx: RenderContext, packets: list[FramePacket]
    ) -> None:
        """Render presentation-only overlays after capture, before present."""
        if not packets:
            return

        drew = False
        for p in self.passes:
            if not isinstance(p, UIPass):
                continue
            p.run(backend, ctx, packets)
            drew = True

        if not drew:
            UIPass().run(backend, ctx, packets)

    def present_frame(self, backend: Backend, ctx: RenderContext) -> None:
        """Present the already-rendered frame to the user."""
        ended = False
        for p in self.passes:
            if not isinstance(p, EndFramePass):
                continue
            p.run(backend, ctx, [])
            ended = True

        if not ended:
            backend.render.end_frame()

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

        world_transform = viewport_transform_for_packet(viewport_state, packet)
        backend.set_viewport_transform(
            viewport_state.offset_x,
            viewport_state.offset_y,
            viewport_state.scale,
        )

        backend.render.set_clip_rect(
            0,
            0,
            viewport_state.virtual_w,
            viewport_state.virtual_h,
        )

        try:
            backend.set_viewport_transform(
                world_transform.ox,
                world_transform.oy,
                world_transform.s,
            )
            for op in packet.ops:
                op(backend)
        finally:
            backend.render.clear_clip_rect()
            backend.clear_viewport_transform()
