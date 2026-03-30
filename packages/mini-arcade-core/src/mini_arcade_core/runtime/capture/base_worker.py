"""
Base worker thread for capture tasks.
"""

from __future__ import annotations

from dataclasses import dataclass
from queue import Empty, Queue
from threading import Event, Thread
from time import monotonic, sleep


@dataclass(frozen=True)
class BaseJob:
    """
    Base job for worker threads.

    :ivar job_id (str): Unique identifier for the job.
    """

    job_id: str


class BaseWorker:
    """Base worker thread for capture tasks."""

    _thread: Thread
    _stop: Event
    _q: Queue[BaseJob]

    def start(self):
        """Start the capture worker thread."""
        if self._thread.is_alive():
            return
        self._stop.clear()
        self._thread.start()

    def stop(self):
        """Stop the capture worker thread."""
        self._stop.set()
        if self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def enqueue(self, job: BaseJob) -> bool:
        """
        Enqueue a capture job.

        :param job: CaptureJob to enqueue.
        :type job: CaptureJob
        :return: True if the job was enqueued successfully, False otherwise.
        :rtype: bool
        """
        if self._stop.is_set():
            return False
        try:
            self._q.put_nowait(job)
            return True
        # Justification: Queue.put_nowait can raise a broad exception
        # pylint: disable=broad-exception-caught
        except Exception:
            return False
        # pylint: enable=broad-exception-caught

    def qsize(self) -> int:
        """Query the current size of the job queue."""
        return self._q.qsize()

    def wait_until_idle(self, timeout_seconds: float | None = None) -> bool:
        """
        Block until the worker queue has finished processing all queued jobs.

        :param timeout_seconds: Optional timeout in seconds.
        :type timeout_seconds: float | None
        :return: True if the queue drained before the timeout, False otherwise.
        :rtype: bool
        """
        deadline = (
            None
            if timeout_seconds is None
            else monotonic() + max(0.0, float(timeout_seconds))
        )
        while True:
            if getattr(self._q, "unfinished_tasks", 0) <= 0:
                return True
            if deadline is not None and monotonic() >= deadline:
                return False
            sleep(0.01)

    def _run(self):
        while not self._stop.is_set():
            try:
                job = self._q.get(timeout=0.1)
                self._process_job(job)
            except Empty:
                continue

    def _process_job(self, job: BaseJob):
        """Process a single job. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement _process_job()")
