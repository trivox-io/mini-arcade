"""
Module for Size2D class.
"""

from __future__ import annotations

from dataclasses import dataclass


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
