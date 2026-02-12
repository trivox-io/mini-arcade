"""
Game configuration classes.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from mini_arcade_core.backend import Backend


@dataclass
class PostFXConfig:
    """
    Configuration for post-processing effects.

    :ivar enabled (bool): Whether post effects are enabled by default.
    :ivar active (list[str]): List of active effect IDs by default.
    """

    enabled: bool = True
    active: list[str] = field(default_factory=list)


@dataclass
class GameConfig:
    """
    Configuration options for the Game.

    :ivar initial_scene (str): Identifier of the initial scene to load.
    :ivar fps (int): Target frames per second.
    :ivar backend (Backend | None): Optional Backend instance to use for rendering and input.
    :ivar postfx (PostFXConfig): Configuration for post-processing effects.
    """

    initial_scene: str = "main"
    fps: int = 60
    backend: Backend | None = None
    postfx: PostFXConfig = field(default_factory=PostFXConfig)
    enable_profiler: bool = False
