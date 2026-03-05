"""
Capture worker thread for saving screenshots.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from queue import Queue
from threading import Event, Thread
from typing import Callable, Optional

from PIL import Image

from mini_arcade_core.runtime.capture.base_worker import BaseJob, BaseWorker
from mini_arcade_core.utils import logger


# pylint: disable=too-many-instance-attributes
@dataclass(frozen=True)
class CaptureJob(BaseJob):
    """
    Job representing a screenshot to be saved.

    :ivar job_id (str): Unique identifier for the capture job.
    :ivar out_path (Path): Destination path for the saved screenshot.
    :ivar bmp_path (Path): Temporary path of the bitmap image to be saved.
    """

    out_path: Path
    bmp_path: Path | None = None
    w: int = 0
    h: int = 0
    pixels: bytes | None = None  # raw pixels
    fmt: str = "BGRA"  # or "ARGB" / "RGBA" depending on what you return
    pitch: int | None = None


@dataclass(frozen=True)
class CaptureResult:
    """
    Result of a completed capture job.

    :ivar job_id (str): Unique identifier for the capture job.
    :ivar out_path (Path): Destination path where the screenshot was saved.
    :ivar ok (bool): Whether the capture was successful.
    :ivar error (Optional[str]): Error message if the capture failed.
    """

    job_id: str
    out_path: Path
    ok: bool
    error: str | None = None


@dataclass
class WorkerConfig:
    """
    Configuration options for the CaptureWorker.

    :ivar queue_size (int): Maximum number of jobs to queue.
    :ivar on_done (Optional[Callable[[CaptureResult], None]]):
        Optional callback invoked when a job is done.
    :ivar name (str): Name of the worker thread.
    :ivar daemon (bool): Whether the thread is a daemon thread.
    :ivar delete_temp (bool): Whether to delete temporary bitmap files after saving.
    """

    queue_size: int = 64
    on_done: Optional[Callable[[CaptureResult], None]] = None
    name: str = "capture-worker"
    daemon: bool = True
    delete_temp: bool = True


class CaptureWorker(BaseWorker):
    """Capture worker thread for saving screenshots asynchronously."""

    def __init__(
        self,
        worker_config: WorkerConfig | None = None,
    ):
        """
        :param queue_size: Maximum number of jobs to queue.
        :type queue_size: int
        :param on_done: Optional callback invoked when a job is done.
        :type on_done: Optional[Callable[[CaptureResult], None]]
        :param name: Name of the worker thread.
        :type name: str
        :param daemon: Whether the thread is a daemon thread.
        :type daemon: bool
        :param delete_temp: Whether to delete temporary bitmap files after saving.
        :type delete_temp: bool
        """
        if worker_config is None:
            worker_config = WorkerConfig()
        self._q: Queue[CaptureJob] = Queue(maxsize=worker_config.queue_size)
        self._stop = Event()
        self._thread = Thread(
            target=self._run,
            name=worker_config.name,
            daemon=worker_config.daemon,
        )
        self._on_done = worker_config.on_done
        self._delete_temp = worker_config.delete_temp

    def set_on_done(
        self, on_done: Optional[Callable[[CaptureResult], None]]
    ) -> None:
        """
        Replace the completion callback invoked after each processed job.
        """
        self._on_done = on_done

    def _process_job(self, job: CaptureJob) -> None:
        try:
            job.out_path.parent.mkdir(parents=True, exist_ok=True)

            if job.bmp_path and job.bmp_path.exists():
                # Load BMP from disk
                img = Image.open(str(job.bmp_path))
            else:
                img = Image.frombuffer(
                    "RGBA",
                    (job.w, job.h),
                    job.pixels,
                    "raw",
                    job.fmt,  # "BGRA" is common on Windows
                    job.pitch or 0,
                    1,
                )
            img.save(str(job.out_path))

            if self._delete_temp:
                try:
                    job.bmp_path.unlink(missing_ok=True)
                except Exception:  # pylint: disable=broad-exception-caught
                    logger.warning(
                        f"Failed to delete temp bmp: {job.bmp_path}"
                    )

            res = CaptureResult(
                job_id=job.job_id, out_path=job.out_path, ok=True
            )

        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.exception("CaptureWorker failed to save screenshot")
            res = CaptureResult(
                job_id=job.job_id,
                out_path=job.out_path,
                ok=False,
                error=str(exc),
            )

        if self._on_done:
            try:
                self._on_done(res)
            except Exception:  # pylint: disable=broad-exception-caught
                logger.warning("CaptureWorker on_done callback failed")

        self._q.task_done()
