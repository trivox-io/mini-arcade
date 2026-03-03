"""
Module for Kinematic2D class.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from mini_arcade_core.spaces.geometry.transform import Transform2D
from mini_arcade_core.spaces.math.vec2 import Vec2


@dataclass
class Kinematic2D:
    """
    Simple 2D kinematic body.

    :ivar velocity: The velocity of the body.
    :ivar accel: The acceleration of the body.
    :ivar max_speed: The maximum speed of the body.
    """

    velocity: Vec2 = field(default_factory=lambda: Vec2(0.0, 0.0))
    accel: Vec2 = field(default_factory=lambda: Vec2(0.0, 0.0))
    max_speed: float = 0.0

    def step(self, transform: Transform2D, dt: float) -> None:
        """
        Move the body according to its velocity and acceleration.

        :param transform: The transform of the body to update.
        :type transform: Transform2D
        :param dt: The time delta to step the body.
        :type dt: float
        """
        self.velocity.x += self.accel.x * dt
        self.velocity.y += self.accel.y * dt

        # max_speed <= 0 means "no speed cap"
        if self.max_speed is not None and self.max_speed > 0.0:
            mag2 = (
                self.velocity.x * self.velocity.x
                + self.velocity.y * self.velocity.y
            )
            if mag2 > (self.max_speed * self.max_speed):
                mag = mag2**0.5
                s = self.max_speed / mag
                self.velocity.x *= s
                self.velocity.y *= s

        transform.center.x += self.velocity.x * dt
        transform.center.y += self.velocity.y * dt

    def stop(self) -> None:
        """
        Stop the body by setting its velocity to zero.
        """
        self.velocity.x = 0.0
        self.velocity.y = 0.0
