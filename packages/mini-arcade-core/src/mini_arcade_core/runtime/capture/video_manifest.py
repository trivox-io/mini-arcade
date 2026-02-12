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
    :ivar capture_fps (int): Frames per second at which frames were captured.
    :ivar frames (int): Total number of frames captured.
    """

    run_id: str
    fps: int
    capture_fps: int
    frames: int = 0
