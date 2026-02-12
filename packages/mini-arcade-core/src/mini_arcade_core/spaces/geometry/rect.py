"""
Module for Rect class.
"""

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade_core.spaces.geometry.size import Size2D
from mini_arcade_core.spaces.math.vec2 import Vec2


@dataclass
class Rect:
    """
    Simple 2D rectangle.
    """

    position: Vec2
    size: Size2D

    @property
    def left(self) -> float:
        """
        Left boundary of the rectangle.

        :return: Left boundary.
        :rtype: float
        """
        return self.position.x

    @property
    def top(self) -> float:
        """
        Top boundary of the rectangle.

        :return: Top boundary.
        :rtype: float
        """
        return self.position.y

    @property
    def right(self) -> float:
        """
        Right boundary of the rectangle.

        :return: Right boundary.
        :rtype: float
        """
        return self.position.x + self.size.width

    @property
    def bottom(self) -> float:
        """
        Bottom boundary of the rectangle.

        :return: Bottom boundary.
        :rtype: float
        """
        return self.position.y + self.size.height

    def overlaps(self, other: "Rect", *, inclusive: bool = False) -> bool:
        """
        Check if this rectangle overlaps with another rectangle.

        :param other: The other rectangle to check against.
        :type other: Rect
        :param inclusive: Whether to consider touching edges as overlapping.
        :type inclusive: bool
        :return: True if the rectangles overlap.
        :rtype: bool
        """
        if inclusive:
            return not (
                self.right < other.left
                or self.left > other.right
                or self.bottom < other.top
                or self.top > other.bottom
            )
        return not (
            self.right <= other.left
            or self.left >= other.right
            or self.bottom <= other.top
            or self.top >= other.bottom
        )
