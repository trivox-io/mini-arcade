"""
2D collision detection helpers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from .geometry2d import Position2D, Size2D


class Collider2D(ABC):
    """
    Abstract base class for 2D colliders.
    """

    position: Position2D
    size: Size2D

    @abstractmethod
    def intersects(self, other: Collider2D) -> bool:
        """
        Check if this collider intersects with another collider.

        :param other: The other collider to check against.
        :type other: Collider2D

        :return: True if the colliders intersect.
        :rtype: bool
        """


@dataclass
class RectCollider(Collider2D):
    """
    OOP collision helper that wraps a Position2D + Size2D pair.

    It does NOT own the data - it just points to them. If the
    entity moves (position changes), the collider “sees” it.

    :ivar position (Position2D): Top-left position of the rectangle.
    :ivar size (Size2D): Size of the rectangle.
    """

    position: Position2D
    size: Size2D

    def intersects(self, other: "RectCollider") -> bool:
        """
        High-level OOP method to check collision with another collider.

        ;param other: The other rectangle collider.
        :type other: RectCollider

        :return: True if the rectangles intersect.
        :rtype: bool
        """
        pos_a = self.position
        size_a = self.size
        pos_b = other.position
        size_b = other.size
        return not (
            pos_a.x + size_a.width < pos_b.x
            or pos_a.x > pos_b.x + size_b.width
            or pos_a.y + size_a.height < pos_b.y
            or pos_a.y > pos_b.y + size_b.height
        )
