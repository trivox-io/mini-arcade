"""
Module for Transform2D class.
"""

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade_core.spaces.geometry.size import Size2D
from mini_arcade_core.spaces.math.vec2 import Vec2


@dataclass
class Transform2D:
    """
    Simple 2D transform with center and size.

    :ivar center: The center of the transform.
    :ivar size: The size of the transform.
    """

    center: Vec2
    size: Size2D
