"""
Module for Vec2 class.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Vec2:
    """
    Simple 2D vector.

    :ivar x (float): X coordinate.
    :ivar y (float): Y coordinate.
    """

    x: float
    y: float

    def to_tuple(self) -> tuple[float, float]:
        """
        Convert Vex2 to a tuple.

        :return: Tuple of (x, y).
        :rtype: tuple[float, float]
        """
        return (self.x, self.y)

    def __add__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar: float) -> "Vec2":
        return Vec2(self.x * scalar, self.y * scalar)

    def __iadd__(self, other: "Vec2") -> "Vec2":
        self.x += other.x
        self.y += other.y
        return self

    def __imul__(self, scalar: float) -> "Vec2":
        self.x *= scalar
        self.y *= scalar
        return self
