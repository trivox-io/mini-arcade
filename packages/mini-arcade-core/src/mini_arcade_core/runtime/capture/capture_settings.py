"""
Capture settings dataclass
"""

from __future__ import annotations

from dataclasses import dataclass


# pylint: disable=too-many-instance-attributes
@dataclass
class CaptureSettings:
    """
    Settings for the Capture Service.

    :ivar screenshots_dir: Directory to save screenshots.
    :ivar screenshots_ext: File extension/format for screenshots.
    :ivar replays_dir: Directory to save replays.
    :ivar recordings_dir: Directory to save video recordings.
    :ivar ffmpeg_path: Path to the ffmpeg executable.
    :ivar encode_on_stop: Whether to encode video on stop.
    :ivar keep_frames: Whether to keep raw frames after encoding.
    :ivar video_codec: Video codec to use for encoding.
    :ivar video_crf: Constant Rate Factor for video quality.
    :ivar video_preset: Preset for video encoding speed/quality tradeoff.
    """

    screenshots_dir: str = "screenshots"
    screenshots_ext: str = "png"
    replays_dir: str = "replays"
    recordings_dir: str = "recordings"
    ffmpeg_path: str = "ffmpeg"  # rely on PATH by default
    encode_on_stop: bool = True
    keep_frames: bool = True
    video_codec: str = "libx264"
    video_crf: int = 18
    video_preset: str = "veryfast"
