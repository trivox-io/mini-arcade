"""
Frame packet for rendering.
"""

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade_core.engine.render.packet import RenderPacket


@dataclass(frozen=True)
class FramePacket:
    """
    A packet representing a frame to be rendered, associated with a specific scene
    and indicating whether it is an overlay.


    :ivar scene_id (str): Identifier of the scene.
    :ivar is_overlay (bool): Whether the frame is an overlay.
    :ivar packet (RenderPacket): The render packet containing rendering operations.
    """

    scene_id: str
    is_overlay: bool
    packet: RenderPacket
