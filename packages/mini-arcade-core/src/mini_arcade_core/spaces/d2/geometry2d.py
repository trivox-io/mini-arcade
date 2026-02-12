"""
2D geometry data structures.
"""

# Justification: This module is deprecated and will be removed in favor of the new geometry module.
# pylint: disable=deprecated-module
# pylint: disable=duplicate-code

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Position2D:
    """
    Simple 2D position.

    :ivar x (float): X coordinate.
    :ivar y (float): Y coordinate.
    """

    x: float
    y: float

    def to_tuple(self) -> tuple[float, float]:
        """
        Convert Position2D to a tuple.

        :return: Tuple of (x, y).
        :rtype: tuple[float, float]
        """
        return (self.x, self.y)


@dataclass
class Size2D:
    """
    Simple 2D size.

    :ivar width (int): Width.
    :ivar height (int): Height.
    """

    width: int
    height: int

    def to_tuple(self) -> tuple[int, int]:
        """
        Convert Size2D to a tuple.

        :return: Tuple of (width, height).
        :rtype: tuple[int, int]
        """
        return (self.width, self.height)


@dataclass
class Bounds2D:
    """
    Axis-aligned rectangular bounds in world space.
    (left, top) .. (right, bottom)

    :ivar left (float): Left boundary.
    :ivar top (float): Top boundary.
    :ivar right (float): Right boundary.
    :ivar bottom (float): Bottom boundary.
    """

    left: float
    top: float
    right: float
    bottom: float

    @classmethod
    def from_size(cls, size: "Size2D") -> "Bounds2D":
        """
        Convenience factory for screen/world bounds starting at (0, 0).

        :param size: Size2D defining the bounds.
        :type size: Size2D

        :return: Bounds2D from (0,0) to (size.width, size.height).
        :rtype: Bounds2D
        """
        return cls(
            left=0.0,
            top=0.0,
            right=float(size.width),
            bottom=float(size.height),
        )
