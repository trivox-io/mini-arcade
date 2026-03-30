"""
Manifest for a captured video session.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VideoManifest:
    """
    Manifest for a captured video session.

    :ivar run_id (str): Unique identifier for the capture session.
    :ivar fps (int): Frames per second of the captured video.
    :ivar capture_fps (float): Target frames per second requested for capture.
    :ivar frames (int): Total number of frames captured.
    :ivar duration_seconds (float): Real elapsed duration of the capture run.
    :ivar effective_capture_fps (float): Observed capture cadence based on frames/duration.
    """

    run_id: str
    fps: int
    capture_fps: float
    frames: int = 0
    duration_seconds: float = 0.0
    effective_capture_fps: float = 0.0
