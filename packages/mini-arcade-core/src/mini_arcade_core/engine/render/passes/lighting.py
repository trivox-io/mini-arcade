"""
Lighting render pass implementation.
"""

from dataclasses import dataclass

from mini_arcade_core.backend import Backend
from mini_arcade_core.engine.render.context import RenderContext
from mini_arcade_core.engine.render.packet import RenderPacket


@dataclass
class LightingPass:
    """
    Lighting Render Pass.
    This pass handles scene lighting effects.
    """

    name: str = "LightingPass"

    # Justification: No implementation yet
    # pylint: disable=unused-argument
    def run(
        self, backend: Backend, ctx: RenderContext, packets: list[RenderPacket]
    ):
        """Run the lighting render pass."""
        # hook/no-op for now
        return
