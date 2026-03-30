"""
Video recording management.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from uuid import uuid4


@dataclass
class VideoRecordConfig:
    """
    Configuration for video recording.

    :ivar fps (int): Desired output frames per second.
    :ivar capture_fps (int): Actual capture frames per second to reduce stalls.
    :ivar ext (str): File extension for saved frames.
    :ivar frames_dir (str): Directory to save recorded frames.
    :ivar prefix (str): Prefix for recording session directories.
    """

    fps: int = 60  # desired output fps in manifest
    capture_fps: int = 60  # actual capture rate to reduce stalls
    ext: str = "png"
    frames_dir: str = "recordings"
    prefix: str = "run_"


class VideoRecorder:
    """Video recording management."""

    def __init__(self, cfg: VideoRecordConfig | None = None):
        """
        :param cfg: Configuration for video recording.
        :type cfg: VideoRecordConfig | None
        """
        self.cfg = cfg or VideoRecordConfig()
        self.active: bool = False
        self.run_id: str = ""
        self.base_dir: Path | None = None
        self.frames_dir_path: Path | None = None

        self._frame_index: int = 0
        self._every_n: int = 1

    @staticmethod
    def _slugify(text: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", str(text or "").strip().lower())
        slug = slug.strip("-")
        return slug or "capture"

    def start(
        self,
        *,
        out_dir: Path | None = None,
        label: str | None = None,
    ) -> Path:
        """
        Start video recording.

        :param out_dir: Optional output directory for recorded frames.
        :type out_dir: Path | None
        :return: Path to the directory where video frames are saved.
        :rtype: Path
        """
        if self.active:
            raise RuntimeError("VideoRecorder already active")

        self.active = True
        self.run_id = uuid4().hex
        timestamp = datetime.now()
        dated_root = out_dir or Path(self.cfg.frames_dir)
        folder_name = (
            f"{timestamp.strftime('%Y%m%d-%H%M%S')}-"
            f"{self._slugify(label or 'capture')}-"
            f"{self.run_id[:6]}"
        )
        self.base_dir = (
            dated_root / timestamp.strftime("%Y-%m-%d") / folder_name
        )
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.frames_dir_path = self.base_dir / "raw" / "frames"
        self.frames_dir_path.mkdir(parents=True, exist_ok=True)

        # reduce load by capturing less frequently
        # example: game 60fps, capture_fps 15 => every 4 frames
        self._every_n = max(
            1, int(round(self.cfg.fps / max(1, self.cfg.capture_fps)))
        )
        self._frame_index = 0
        return self.base_dir

    def stop(self) -> None:
        """Stop video recording."""
        self.active = False
        self.run_id = ""
        self.base_dir = None
        self.frames_dir_path = None
        self._frame_index = 0

    def should_capture(self, frame_index: int) -> bool:
        """
        Check if the current frame index should be captured based on the
        capture frequency.

        :param frame_index: The current frame index.
        :type frame_index: int
        :return: True if the frame should be captured, False otherwise.
        :rtype: bool
        """
        return self.active and (frame_index % self._every_n == 0)

    def next_paths(self) -> tuple[Path, Path, int]:
        """
        Returns: (tmp_bmp_path, out_png_path, out_frame_index)
        out_frame_index increases only when we actually capture.

        :param frame_index: The current frame index.
        :type frame_index: int
        :raise: RuntimeError: If the recorder is not active.
        """
        if (
            not self.active
            or self.base_dir is None
            or self.frames_dir_path is None
        ):
            raise RuntimeError("VideoRecorder is not active")

        out_frame = self._frame_index
        self._frame_index += 1

        out_png = (
            self.frames_dir_path / f"frame_{out_frame:08d}.{self.cfg.ext}"
        )
        return out_png, out_frame

    def rollback_last_frame(self) -> None:
        """Undo the most recent reserved frame index if capture did not queue."""
        if self._frame_index > 0:
            self._frame_index -= 1
