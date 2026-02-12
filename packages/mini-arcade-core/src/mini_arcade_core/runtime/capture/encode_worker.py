"""
Encode worker thread for processing video encoding jobs.
"""

from __future__ import annotations

import traceback
from dataclasses import dataclass
from pathlib import Path
from queue import Queue
from threading import Event, Thread
from typing import Callable, Optional

from mini_arcade_core.runtime.capture.base_worker import BaseJob, BaseWorker
from mini_arcade_core.runtime.capture.video_encoder import (
    encode_png_sequence_to_mp4,
)
from mini_arcade_core.utils import logger


# pylint: disable=too-many-instance-attributes
@dataclass(frozen=True)
class EncodeJob(BaseJob):
    """
    Job for encoding a sequence of PNG frames into a video file.

    :ivar job_id (str): Unique identifier for the encoding job.
    :ivar ffmpeg_path (str): Path to the ffmpeg executable.
    :ivar frames_dir (Path): Directory containing the PNG frames to encode.
    :ivar output_path (Path): Destination path for the encoded video file.
    :ivar input_fps (int): Frames per second of the input PNG sequence.
    :ivar output_fps (int | None): Frames per second for the output video file.
    :ivar codec (str): Video codec to use for encoding.
    :ivar crf (int): Constant Rate Factor for video quality.
    :ivar preset (str): Preset for video encoding speed/quality tradeoff.
    :ivar keep_frames (bool): Whether to keep raw frames after encoding.
    """

    ffmpeg_path: str
    frames_dir: Path
    output_path: Path
    input_fps: int
    output_fps: int | None
    codec: str
    crf: int
    preset: str
    keep_frames: bool
    video_interpolate: bool = True


@dataclass(frozen=True)
class EncodeResult:
    """
    Result of an encoding job.

    :ivar job_id (str): Unique identifier for the encoding job.
    :ivar ok (bool): Whether the encoding was successful.
    :ivar output_path (Path | None): Path to the encoded video file if successful.
    :ivar error (str | None): Error message if the encoding failed.
    """

    job_id: str
    ok: bool
    output_path: Path | None = None
    error: str | None = None


@dataclass
class EncodeWorkerConfig:
    """
    Configuration options for the EncodeWorker.

    :ivar queue_size (int): Maximum number of jobs to queue.
    :ivar on_done (Optional[Callable[[EncodeResult], None]]):
        Optional callback invoked when a job is done.
    :ivar name (str): Name of the worker thread.
    :ivar daemon (bool): Whether the thread is a daemon thread.
    """

    queue_size: int = 4
    on_done: Optional[Callable[[EncodeResult], None]] = None
    name: str = "encode-worker"
    daemon: bool = True


class EncodeWorker(BaseWorker):
    """Encode worker thread for processing video encoding jobs asynchronously."""

    def __init__(self, cfg: EncodeWorkerConfig | None = None):
        """
        :param cfg: Optional configuration for the EncodeWorker.
        :type cfg: Optional[EncodeWorkerConfig]
        """
        cfg = cfg or EncodeWorkerConfig()
        self._q: Queue[EncodeJob] = Queue(maxsize=cfg.queue_size)
        self._stop = Event()
        self._on_done = cfg.on_done
        self._thread = Thread(
            target=self._run, name=cfg.name, daemon=cfg.daemon
        )

    def _process_job(self, job: EncodeJob) -> None:
        try:
            logger.info(f"[encode] job={job.job_id} start {job.output_path}")
            result = encode_png_sequence_to_mp4(
                ffmpeg_path=job.ffmpeg_path,
                frames_dir=job.frames_dir,
                output_path=job.output_path,
                input_fps=job.input_fps,
                output_fps=job.output_fps,
                codec=job.codec,
                crf=job.crf,
                preset=job.preset,
            )

            if not result.ok:
                res = EncodeResult(
                    job_id=job.job_id, ok=False, error=result.error
                )
            else:
                # optionally delete frames after successful encode
                if not job.keep_frames:
                    for p in job.frames_dir.glob("frame_*.png"):
                        p.unlink(missing_ok=True)
                res = EncodeResult(
                    job_id=job.job_id,
                    ok=True,
                    output_path=result.output_path,
                )

        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error(
                f"[encode] exception: {exc}\n{traceback.format_exc()}"
            )
            res = EncodeResult(job_id=job.job_id, ok=False, error=str(exc))

        if self._on_done:
            try:
                self._on_done(res)
            except Exception:  # pylint: disable=broad-exception-caught
                logger.warning("[encode] on_done callback failed")

        self._q.task_done()
