"""
Animation module for handling frame-based animations in the mini arcade engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Sequence, TypeVar

# pylint: disable=invalid-name
TFrame = TypeVar("TFrame")
# pylint: enable=invalid-name


@dataclass
class Animation(Generic[TFrame]):
    """
    Simple animation class that cycles through frames at a specified FPS.

    :ivar frames (Sequence[TFrame]): The frames of the animation.
    :ivar fps (float): Frames per second for the animation.
    :ivar loop (bool): Whether the animation should loop.
    :ivar time (float): Internal timer to track frame changes.
    :ivar index (int): Current frame index.
    """

    frames: Sequence[TFrame]
    fps: float = 10.0
    loop: bool = True
    time: float = 0.0
    index: int = 0

    def update(self, dt: float) -> None:
        """
        Update the animation based on the elapsed time.

        :param dt: Time elapsed since the last update (in seconds).
        :type dt: float
        """
        self.time += dt
        frame_time = 1.0 / self.fps
        while self.time >= frame_time:
            self.time -= frame_time
            self.index += 1
            if self.index >= len(self.frames):
                self.index = 0 if self.loop else len(self.frames) - 1

    @property
    def current_frame(self) -> TFrame:
        """
        Get the current frame of the animation.

        :return: The current frame.
        :rtype: TFrame
        """
        return self.frames[self.index]
