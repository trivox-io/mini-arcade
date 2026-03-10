"""
Procedural textures used by the entity tutorial examples.
"""

from __future__ import annotations

from typing import Callable


Color = tuple[int, int, int, int]


def _clamp_channel(value: int) -> int:
    return max(0, min(255, int(value)))


def _pack_rgba(
    width: int,
    height: int,
    pixel_fn: Callable[[int, int], Color],
) -> bytes:
    out = bytearray()
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixel_fn(x, y)
            out.extend(
                (
                    _clamp_channel(r),
                    _clamp_channel(g),
                    _clamp_channel(b),
                    _clamp_channel(a),
                )
            )
    return bytes(out)


def create_texture(
    backend_render: object,
    *,
    width: int,
    height: int,
    pixel_fn: Callable[[int, int], Color],
) -> int:
    """
    Upload a procedural RGBA texture through the backend render port.
    """
    pixels = _pack_rgba(width, height, pixel_fn)
    return int(
        backend_render.create_texture_rgba(width, height, pixels, width * 4)
    )


def checker_texture(
    backend_render: object,
    *,
    width: int,
    height: int,
    color_a: Color,
    color_b: Color,
    cell: int = 4,
) -> int:
    return create_texture(
        backend_render,
        width=width,
        height=height,
        pixel_fn=lambda x, y: (
            color_a
            if ((x // cell) + (y // cell)) % 2 == 0
            else color_b
        ),
    )


def diamond_texture(
    backend_render: object,
    *,
    size: int,
    fill: Color,
    outline: Color,
    background: Color = (0, 0, 0, 0),
) -> int:
    half = size / 2.0

    def _pixel(x: int, y: int) -> Color:
        dist = abs(x + 0.5 - half) + abs(y + 0.5 - half)
        if dist <= half - 1.5:
            return fill
        if dist <= half:
            return outline
        return background

    return create_texture(
        backend_render,
        width=size,
        height=size,
        pixel_fn=_pixel,
    )


def stripe_texture(
    backend_render: object,
    *,
    width: int,
    height: int,
    base: Color,
    stripe: Color,
    stripe_width: int = 3,
) -> int:
    return create_texture(
        backend_render,
        width=width,
        height=height,
        pixel_fn=lambda x, _y: (
            stripe if (x // stripe_width) % 2 == 0 else base
        ),
    )


def orb_frame_texture(
    backend_render: object,
    *,
    size: int,
    inner: Color,
    outer: Color,
    background: Color = (0, 0, 0, 0),
) -> int:
    center = (size - 1) / 2.0
    outer_radius = size * 0.45
    inner_radius = size * 0.24

    def _pixel(x: int, y: int) -> Color:
        dx = x - center
        dy = y - center
        dist2 = (dx * dx) + (dy * dy)
        if dist2 <= inner_radius * inner_radius:
            return inner
        if dist2 <= outer_radius * outer_radius:
            return outer
        return background

    return create_texture(
        backend_render,
        width=size,
        height=size,
        pixel_fn=_pixel,
    )

