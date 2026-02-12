"""
Viewport transformation utilities.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ViewportTransform:
    """
    Viewport transformation for coordinate mapping.

    :ivar ox (int): Origin x-coordinate.
    :ivar oy (int): Origin y-coordinate.
    :ivar s (float): Scaling factor.
    """

    ox: int = 0
    oy: int = 0
    s: float = 1.0

    def map_xy(self, x: int, y: int) -> tuple[int, int]:
        """
        Map the given (x, y) coordinates using the viewport transformation.

        :param x: The x-coordinate to map.
        :type x: int
        :param y: The y-coordinate to map.
        :type y: int
        :return: A tuple containing the mapped (x, y) coordinates.
        :rtype: tuple[int, int]
        """
        return (
            int(round(self.ox + x * self.s)),
            int(round(self.oy + y * self.s)),
        )

    def map_wh(self, w: int, h: int) -> tuple[int, int]:
        """
        Map the given width and height using the viewport transformation.

        :param w: The width to map.
        :type w: int
        :param h: The height to map.
        :type h: int
        :return: A tuple containing the mapped (width, height).
        :rtype: tuple[int, int]
        """
        return (int(round(w * self.s)), int(round(h * self.s)))
