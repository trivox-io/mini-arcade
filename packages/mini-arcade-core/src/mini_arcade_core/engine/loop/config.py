"""
Game core module defining the Game class and configuration.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RunnerConfig:
    """
    Configuration for the main loop runner.

    :ivar fps (int): Target frames per second (0 for uncapped).
    :ivar max_frames (int | None): Optional maximum number of frames to run (None for unlimited).
    """

    fps: int = 60
    max_frames: int | None = None
