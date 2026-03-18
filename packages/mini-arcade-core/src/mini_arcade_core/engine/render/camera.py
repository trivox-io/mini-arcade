"""
Camera helpers for world-space rendering.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from mini_arcade_core.backend.viewport import ViewportTransform
from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.engine.render.viewport import ViewportState
from mini_arcade_core.spaces.math.vec2 import Vec2

CAMERA_PACKET_META_KEY = "camera_2d"


@dataclass
class Camera2D:
    """
    Minimal 2D camera model for world-space rendering.

    `center` is expressed in virtual/world coordinates and maps to the center
    of the virtual viewport. `zoom=1.0` means 1:1 virtual scale.
    """

    center: Vec2 = field(default_factory=lambda: Vec2(0.0, 0.0))
    zoom: float = 1.0


def _normalized_zoom(camera: Camera2D | None) -> float:
    if camera is None:
        return 1.0
    return max(0.001, float(camera.zoom))


def viewport_transform_for_camera(
    viewport: ViewportState,
    camera: Camera2D | None = None,
) -> ViewportTransform:
    """
    Build the world-space transform for one viewport/camera pair.
    """

    if camera is None:
        return ViewportTransform(
            ox=int(viewport.offset_x),
            oy=int(viewport.offset_y),
            s=float(viewport.scale),
        )

    zoom = _normalized_zoom(camera)
    scale = float(viewport.scale) * zoom
    ox = (
        float(viewport.offset_x)
        + (float(viewport.virtual_w) * float(viewport.scale) * 0.5)
        - (float(camera.center.x) * scale)
    )
    oy = (
        float(viewport.offset_y)
        + (float(viewport.virtual_h) * float(viewport.scale) * 0.5)
        - (float(camera.center.y) * scale)
    )
    return ViewportTransform(
        ox=int(round(ox)),
        oy=int(round(oy)),
        s=scale,
    )


def camera_from_packet(packet: RenderPacket) -> Camera2D | None:
    """
    Read an attached camera from packet metadata.
    """

    raw = packet.meta.get(CAMERA_PACKET_META_KEY)
    return raw if isinstance(raw, Camera2D) else None


def viewport_transform_for_packet(
    viewport: ViewportState,
    packet: RenderPacket,
) -> ViewportTransform:
    """
    Build the render transform for one packet, using any attached camera.
    """

    return viewport_transform_for_camera(
        viewport,
        camera_from_packet(packet),
    )


def packet_with_camera(
    packet: RenderPacket,
    camera: Camera2D | None,
) -> RenderPacket:
    """
    Return a copy of a packet with camera metadata attached.
    """

    if camera is None:
        return packet
    meta = dict(packet.meta)
    meta[CAMERA_PACKET_META_KEY] = camera
    return RenderPacket(ops=packet.ops, meta=meta)


def world_to_screen(
    viewport: ViewportState,
    x: float,
    y: float,
    *,
    camera: Camera2D | None = None,
) -> tuple[float, float]:
    """
    Convert world coordinates into screen coordinates.
    """

    transform = viewport_transform_for_camera(viewport, camera)
    return (
        float(transform.ox) + (float(x) * float(transform.s)),
        float(transform.oy) + (float(y) * float(transform.s)),
    )


def screen_to_world(
    viewport: ViewportState,
    x: float,
    y: float,
    *,
    camera: Camera2D | None = None,
) -> tuple[float, float]:
    """
    Convert screen coordinates into world coordinates.
    """

    if camera is None:
        return (
            (float(x) - float(viewport.offset_x)) / float(viewport.scale),
            (float(y) - float(viewport.offset_y)) / float(viewport.scale),
        )

    zoom = _normalized_zoom(camera)
    virtual_x = (float(x) - float(viewport.offset_x)) / float(viewport.scale)
    virtual_y = (float(y) - float(viewport.offset_y)) / float(viewport.scale)
    return (
        ((virtual_x - (float(viewport.virtual_w) * 0.5)) / zoom)
        + float(camera.center.x),
        ((virtual_y - (float(viewport.virtual_h) * 0.5)) / zoom)
        + float(camera.center.y),
    )


__all__ = [
    "CAMERA_PACKET_META_KEY",
    "Camera2D",
    "camera_from_packet",
    "packet_with_camera",
    "screen_to_world",
    "viewport_transform_for_camera",
    "viewport_transform_for_packet",
    "world_to_screen",
]
