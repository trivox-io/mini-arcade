"""
Built-in systems for scenes.
"""

from dataclasses import dataclass

from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.scenes.sim_scene import BaseTickContext


@dataclass
class BaseInputSystem:
    """
    Converts InputFrame -> MenuIntent.

    :ivar name: Name of the system - default is "base_input".
    :ivar order: Execution order of the system - default is 10.
    """

    name: str = "base_input"
    order: int = 10

    def step(self, ctx: BaseTickContext):
        """Step the input system to extract menu intent."""


@dataclass
class BaseRenderSystem:
    """
    Base rendering system.

    :ivar name: Name of the system - default is "base_render".
    :ivar order: Execution order of the system - default is 100.
    """

    name: str = "base_render"
    order: int = 100

    def step(self, ctx: BaseTickContext):
        """Set the render packet to draw the menu."""
        ctx.packet = RenderPacket.from_ops(ctx.draw_ops)
