"""
Geometry shape definitions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from mini_arcade_core.spaces.math.vec2 import Vec2

ShapeKind = Literal["rect", "circle", "triangle", "line", "poly"]


@dataclass
class Shape2D:
    """
    Simple shape entity.

    :ivar kind: The kind of shape (rect, circle, triangle, line, poly).
    """

    kind: ShapeKind


@dataclass
class Rect(Shape2D):
    """
    Rectangle shape entity.

    :ivar kind: The kind of shape (rect).
    :ivar corner_radius: The corner radius of the rectangle.
    """

    kind: Literal["rect"] = "rect"
    corner_radius: float = 0.0


@dataclass
class Circle(Shape2D):
    """
    Circle shape entity.

    :ivar kind: The kind of shape (circle).
    :ivar radius: The radius of the circle.
    """

    kind: Literal["circle"] = "circle"
    radius: float = 0.0


@dataclass
class Triangle(Shape2D):
    """
    Triangle shape entity.

    :ivar kind: The kind of shape (triangle).
    """

    kind: Literal["triangle"] = "triangle"


@dataclass
class Line(Shape2D):
    """
    Line shape entity.

    :ivar kind: The kind of shape (line).
    :ivar a: The start point of the line (local-space).
    :ivar b: The end point of the line (local-space).
    :ivar dash_length: Optional dash length in pixels for dashed rendering.
    :ivar dash_gap: Optional gap length in pixels for dashed rendering.
    """

    kind: Literal["line"] = "line"
    a: Vec2 = field(default_factory=lambda: Vec2(0.0, 0.0))
    b: Vec2 = field(default_factory=lambda: Vec2(0.0, 0.0))
    dash_length: float | None = None
    dash_gap: float | None = None


@dataclass
class Poly(Shape2D):
    """
    Polygon shape entity.

    :ivar kind: The kind of shape (poly).
    :ivar points: The points of the polygon (local-space).
    """

    kind: Literal["poly"] = "poly"
    points: list[Vec2] | None = None
