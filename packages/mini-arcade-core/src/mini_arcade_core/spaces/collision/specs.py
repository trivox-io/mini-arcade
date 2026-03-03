"""
Collision collider specifications.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from mini_arcade_core.spaces.geometry.size import Size2D
from mini_arcade_core.spaces.math.vec2 import Vec2

ColliderKind = Literal["rect", "circle", "poly", "line"]


@dataclass(frozen=True)
class ColliderSpec:
    """
    Simple collider specification.

    :ivar kind: The kind of collider (rect, circle, poly, line).
    """

    kind: ColliderKind


@dataclass(frozen=True)
class RectColliderSpec(ColliderSpec):
    """
    Rectangle collider specification.

    :ivar kind: The kind of collider (rect).
    :ivar size: The size of the rectangle collider. If None, derived from transform.size.
    """

    kind: Literal["rect"] = "rect"
    # if None -> derived from transform.size
    size: Size2D | None = None


@dataclass(frozen=True)
class CircleColliderSpec(ColliderSpec):
    """
    Circle collider specification.

    :ivar kind: The kind of collider (circle).
    :ivar radius: The radius of the circle collider. If None, derived from min(size)/2.
    """

    kind: Literal["circle"] = "circle"
    radius: float | None = None  # if None -> min(size)/2


@dataclass(frozen=True)
class LineColliderSpec(ColliderSpec):
    """
    Line collider specification.

    :ivar kind: The kind of collider (line).
    :ivar a: The start point of the line collider (local-space).
    :ivar b: The end point of the line collider (local-space).
    """

    kind: Literal["line"] = "line"
    a: Vec2 = Vec2(0.0, 0.0)  # local-space
    b: Vec2 = Vec2(1.0, 0.0)


@dataclass(frozen=True)
class PolyColliderSpec(ColliderSpec):
    """
    Polygon collider specification.

    :ivar kind: The kind of collider (poly).
    :ivar points: The points of the polygon collider (local-space).
    """

    kind: Literal["poly"] = "poly"
    points: tuple[Vec2, ...] = ()  # local-space polygon
