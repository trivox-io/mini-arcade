"""
Module for Kinematic2D class.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from mini_arcade_core.spaces.collision.rect_collider import RectCollider
from mini_arcade_core.spaces.geometry.rect import Rect
from mini_arcade_core.spaces.geometry.size import Size2D
from mini_arcade_core.spaces.geometry.transform import Transform2D
from mini_arcade_core.spaces.math.vec2 import Vec2


@dataclass
class Kinematic2D:
    """
    Simple 2D kinematic body.
    """

    transform: Transform2D
    velocity: Vec2 = field(default_factory=lambda: Vec2(0.0, 0.0))
    collider: RectCollider = field(init=False)
    speed: float = 0.0

    def __post_init__(self):
        self.collider = RectCollider(
            self.transform.position, self.transform.size
        )

    def step(self, dt: float) -> None:
        """Move the body according to its velocity and speed."""
        self.transform.move_center_scaled(self.velocity, dt)

    @property
    def rect(self) -> Rect:
        """Get the bounding rectangle of the body."""
        return self.transform.rect

    @property
    def center(self) -> Vec2:
        """Get the center position of the body."""
        return self.transform.center

    @property
    def size(self) -> Size2D:
        """Get the size of the body."""
        return self.transform.size

    @property
    def position(self) -> Vec2:
        """Get the top-left position of the body."""
        return self.transform.position

    @position.setter
    def position(self, pos: Vec2) -> None:
        """Set the top-left position of the body."""
        self.transform.position = pos
