"""
A simple rectangular collider for collision detection.
"""

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade_core.spaces.geometry.shapes import Rect
from mini_arcade_core.spaces.geometry.size import Size2D
from mini_arcade_core.spaces.math.vec2 import Vec2


@dataclass
class RectCollider:
    """
    A simple rectangular collider for collision detection.

    :ivar position (Vec2): Top-left position of the rectangle.
    :ivar size (Size2D): Size of the rectangle.
    """

    position: Vec2
    size: Size2D

    @property
    def rect(self) -> Rect:
        """
        Get the bounding rectangle of the collider.

        :return: Bounding rectangle.
        :rtype: Rect
        """
        return Rect(self.position, self.size)

    def intersects(
        self, other: "RectCollider", *, inclusive: bool = True
    ) -> bool:
        """
        Check if this rectangle collider intersects with another rectangle collider.

        :param other: The other rectangle collider.
        :type other: RectCollider
        :return: True if the rectangles intersect, False otherwise.
        :rtype: bool
        """
        # TODO: Check how is this actually working, because the rect property returns
        # a Rect object, which has the overlaps method.
        # Justification: Disabling no-member because rect is a property that returns
        # a Rect object, which has the overlaps method.
        return self.rect.overlaps(  # pylint: disable=no-member
            other.rect, inclusive=inclusive
        )
