"""
Render pass base protocol.
"""

from __future__ import annotations

from typing import Protocol

from mini_arcade_core.backend import Backend
from mini_arcade_core.engine.render.context import RenderContext
from mini_arcade_core.engine.render.packet import RenderPacket


class RenderPass(Protocol):
    """
    Render pass protocol.

    :ivar name: str: Name of the render pass.
    """

    name: str

    def run(
        self, backend: Backend, ctx: RenderContext, packets: list[RenderPacket]
    ):
        """
        Run the render pass.

        :param backend: Backend: The rendering backend.
        :type backend: Backend

        :param ctx: RenderContext: The rendering context.
        :type ctx: RenderContext

        :param packets: list[RenderPacket]: List of render packets to process.
        :type packets: list[RenderPacket]
        """
