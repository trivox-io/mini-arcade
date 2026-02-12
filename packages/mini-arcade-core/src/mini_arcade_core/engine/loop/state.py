"""
Game core module defining the Game class and configuration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter


@dataclass
class FrameState:
    """
    State of the current frame in the main loop.

    :ivar frame_index (int): The current frame index.
    :ivar last_time (float): The timestamp of the last frame.
    :ivar time_s (float): The total elapsed time in seconds.
    :ivar dt (float): The delta time since the last frame in seconds.
    """

    frame_index: int = 0
    last_time: float = field(default_factory=perf_counter)
    time_s: float = 0.0
    dt: float = 0.0

    def step_time(self):
        """Step the time forward by calculating dt."""
        now = perf_counter()
        self.dt = now - self.last_time
        self.last_time = now
        self.time_s += self.dt
