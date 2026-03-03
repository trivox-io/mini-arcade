"""
Boundary behaviors for 2D rectangular objects.

This module is transitional:
- Supports the legacy d2 model (`position`, `size`, `velocity`)
- Supports the new model (`transform`, `kinematic`)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from mini_arcade_core.spaces.geometry.transform import Transform2D
from mini_arcade_core.spaces.physics.kinematics2d import Kinematic2D

from ..geometry.bounds import Bounds2D, Position2D, Size2D
from .physics2d import Velocity2D


class LegacyRectKinematic(Protocol):
    """
    Legacy contract for something that can bounce.
    """

    position: Position2D
    size: Size2D
    velocity: Velocity2D


class RectKinematic(Protocol):
    """
    New contract for something that can bounce.

    Note:
    - In the current engine usage, `transform.center` is treated as top-left.
    """

    transform: Transform2D
    kinematic: Kinematic2D


@dataclass
class VerticalBounce:
    """
    Bounce an object off the top/bottom bounds by inverting vertical velocity
    and clamping its position inside bounds.
    """

    bounds: Bounds2D

    def apply(self, obj: RectKinematic | LegacyRectKinematic) -> bool:
        """
        Apply vertical bounce to the given object.
        """
        top = self.bounds.top
        bottom = self.bounds.bottom
        bounced = False

        # New model
        if hasattr(obj, "transform") and hasattr(obj, "kinematic"):
            if obj.kinematic is None:
                return False

            y = obj.transform.center.y
            h = obj.transform.size.height

            if y <= top:
                y = top
                obj.kinematic.velocity.y *= -1
                bounced = True

            if y + h >= bottom:
                y = bottom - h
                obj.kinematic.velocity.y *= -1
                bounced = True

            obj.transform.center.y = y
            return bounced

        # Legacy model
        if obj.position.y <= top:
            obj.position.y = top
            obj.velocity.vy *= -1
            bounced = True

        if obj.position.y + obj.size.height >= bottom:
            obj.position.y = bottom - obj.size.height
            obj.velocity.vy *= -1
            bounced = True

        return bounced


class LegacyRectSprite(Protocol):
    """
    Legacy contract for something that can wrap.
    """

    position: Position2D
    size: Size2D


class RectSprite(Protocol):
    """
    New contract for something that can wrap.
    """

    transform: Transform2D


@dataclass
class VerticalWrap:
    """
    Wrap an object top <-> bottom.
    """

    bounds: Bounds2D

    def apply(self, obj: RectSprite | LegacyRectSprite) -> None:
        """
        Apply vertical wrap to the given object.
        """
        top = self.bounds.top
        bottom = self.bounds.bottom

        # New model
        if hasattr(obj, "transform"):
            y = obj.transform.center.y
            h = obj.transform.size.height

            if y + h < top:
                obj.transform.center.y = bottom
            elif y > bottom:
                obj.transform.center.y = top - h
            return

        # Legacy model
        if obj.position.y + obj.size.height < top:
            obj.position.y = bottom
        elif obj.position.y > bottom:
            obj.position.y = top - obj.size.height
