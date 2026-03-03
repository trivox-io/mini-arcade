"""
Engine components for mini-arcade-core.
"""

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade_core.engine.animation import Animation


@dataclass
class Sprite2D:
    """
    Simple 2D sprite entity.

    :ivar texture: The texture ID of the sprite.
    """

    texture: int


@dataclass
class Anim2D:
    """
    Simple 2D animation entity.

    :ivar anim: The animation object.
    :ivar texture: The cached current frame of the animation.
    """

    anim: Animation
    texture: int | None = None  # cached current frame

    def step(self, dt: float) -> None:
        """
        Update the animation and cache the current frame.

        :param dt: The time delta to step the animation.
        :type dt: float
        """
        self.anim.update(dt)
        self.texture = self.anim.current_frame


@dataclass
class Life:
    """
    Life component with optional time-to-live.

    :ivar ttl: The time-to-live of the entity. If None, the entity is immortal.
    :ivar alive: Whether the entity is alive or not.
    """

    ttl: float | None = None
    alive: bool = True

    def step(self, dt: float) -> None:
        """
        Update the life component, reducing ttl and setting alive to False if ttl expires.

        :param dt: The time delta to step the life component.
        :type dt: float
        """
        if self.ttl is None or not self.alive:
            return
        self.ttl -= dt
        if self.ttl <= 0:
            self.alive = False
