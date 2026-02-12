"""
End Frame render pass implementation.
"""

from dataclasses import dataclass

from mini_arcade_core.backend import Backend
from mini_arcade_core.engine.render.context import RenderContext
from mini_arcade_core.engine.render.packet import RenderPacket


@dataclass
class EndFramePass:
    """
    End Frame Render Pass.
    This pass signals the end of the current frame to the backend.
    """

    name: str = "EndFrame"

    # Justification: some arguments are unused but required by the protocol
    # pylint: disable=unused-argument
    def run(
        self, backend: Backend, ctx: RenderContext, packets: list[RenderPacket]
    ):
        """Run the end frame pass."""
        # Signal the end of the frame to the backend
        backend.render.end_frame()
