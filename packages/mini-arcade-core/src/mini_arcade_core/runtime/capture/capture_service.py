"""
Capture service managing screenshots and replays.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Optional
from uuid import uuid4

from mini_arcade_core.backend import Backend
from mini_arcade_core.runtime.capture.capture_service_protocol import (
    CaptureServicePort,
)
from mini_arcade_core.runtime.capture.capture_settings import CaptureSettings
from mini_arcade_core.runtime.capture.capture_worker import CaptureJob
from mini_arcade_core.runtime.capture.encode_worker import (
    EncodeJob,
    EncodeWorker,
)
from mini_arcade_core.runtime.capture.replay import (
    ReplayPlayer,
    ReplayRecorder,
    ReplayRecorderConfig,
)
from mini_arcade_core.runtime.capture.replay_format import ReplayHeader
from mini_arcade_core.runtime.capture.screenshot_capturer import (
    ScreenshotCapturer,
)
from mini_arcade_core.runtime.capture.video import (
    VideoRecordConfig,
    VideoRecorder,
)
from mini_arcade_core.runtime.capture.video_manifest import VideoManifest
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.utils import logger


# pylint: disable=too-many-instance-attributes
class CaptureService(CaptureServicePort):
    """
    Owns:
        - screenshots (delegated)
        - replay recording (InputFrame stream)
        - replay playback (feeds InputFrames)
        - (later) video recording
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        backend: Backend,
        *,
        screenshots: Optional[ScreenshotCapturer] = None,
        replay_recorder: Optional[ReplayRecorder] = None,
        replay_player: Optional[ReplayPlayer] = None,
        settings: Optional[CaptureSettings] = None,
    ):
        self.backend = backend
        self.settings = settings or CaptureSettings()

        self.screenshots = screenshots or ScreenshotCapturer(backend)
        self.replay_recorder = replay_recorder or ReplayRecorder()
        self.replay_player = replay_player or ReplayPlayer()
        self.video = VideoRecorder(VideoRecordConfig(fps=60, capture_fps=15))
        self._video_manifest: Optional[VideoManifest] = None
        self.encoder = EncodeWorker()
        self.encoder.start()

    # -------- screenshots --------
    def screenshot(self, label: str | None = None) -> str:
        return self.screenshots.screenshot(label)

    def screenshot_sim(
        self, run_id: str, frame_index: int, label: str = "frame"
    ) -> str:
        return self.screenshots.screenshot_sim(run_id, frame_index, label)

    # -------- replays --------
    @property
    def replay_playing(self) -> bool:
        return self.replay_player.active

    @property
    def replay_recording(self) -> bool:
        return self.replay_recorder.active

    def start_replay_record(
        self,
        *,
        filename: str,
        header: ReplayHeader,
    ):
        path = Path(self.settings.replays_dir) / filename
        self.replay_recorder.start(
            ReplayRecorderConfig(path=path, header=header)
        )

    def stop_replay_record(self):
        self.replay_recorder.stop()

    def record_input(self, frame: InputFrame):
        self.replay_recorder.record(frame)

    def start_replay_play(self, filename: str) -> ReplayHeader:
        path = Path(self.settings.replays_dir) / filename
        return self.replay_player.start(path)

    def stop_replay_play(self):
        self.replay_player.stop()

    def next_replay_input(self) -> InputFrame:
        return self.replay_player.next()

    # -------- video --------

    @property
    def video_recording(self) -> bool:
        return self.video.active

    def start_video_record(
        self, *, fps: int = 60, capture_fps: int = 15
    ) -> Path:
        # configure
        self.video.cfg.fps = fps
        self.video.cfg.capture_fps = capture_fps

        base_dir = self.video.start()
        self._video_manifest = VideoManifest(
            run_id=self.video.run_id,
            fps=fps,
            capture_fps=capture_fps,
            frames=0,
        )
        self._write_video_manifest(base_dir)
        return base_dir

    def stop_video_record(self):
        logger.info("Stopping video recording...")

        if not (
            self.video.active and self.video.base_dir and self._video_manifest
        ):
            self.video.stop()
            self._video_manifest = None
            return

        base_dir = self.video.base_dir
        manifest = self._video_manifest

        self._write_video_manifest(base_dir)
        logger.info(f"Video frames saved to: {base_dir}")

        if self.settings.encode_on_stop:
            out_mp4 = base_dir / "video.mp4"

            job = EncodeJob(
                job_id=f"encode:{uuid4().hex}",
                ffmpeg_path=self.settings.ffmpeg_path,
                frames_dir=base_dir,
                output_path=out_mp4,
                input_fps=manifest.capture_fps,
                output_fps=manifest.fps,
                codec=self.settings.video_codec,
                crf=self.settings.video_crf,
                preset=self.settings.video_preset,
                keep_frames=self.settings.keep_frames,
            )

            if not self.encoder.enqueue(job):
                logger.warning("[encode] dropped encode job (queue full)")
            else:
                logger.info(f"[encode] queued → {out_mp4}")

        self.video.stop()
        self._video_manifest = None
        logger.info("Video recording stopped.")

    def record_video_frame(self, *, frame_index: int):
        """
        Call this once per engine frame (from EngineRunner) AFTER render.
        """
        if not self.video.active:
            return
        if not self.video.should_capture(frame_index):
            return

        worker = self.screenshots.worker

        # Backpressure: if worker is overloaded, drop to protect gameplay
        if hasattr(worker, "qsize") and worker.qsize() > 200:
            return

        out_png, out_frame = self.video.next_paths()
        out_png.parent.mkdir(parents=True, exist_ok=True)

        # Capture bytes (no disk I/O on the main thread)
        w, h, pixels = (
            self.backend.capture.argb8888_bytes()
        )  # uses backend.capture.bmp(None)
        # alternatively: data = self.backend.capture.bmp(path=None) if supported

        if self._video_manifest:
            self._video_manifest = VideoManifest(
                run_id=self._video_manifest.run_id,
                fps=self._video_manifest.fps,
                capture_fps=self._video_manifest.capture_fps,
                frames=out_frame + 1,
            )

        job_id = f"video:{self.video.run_id}:{out_frame}"
        if not worker.enqueue(
            CaptureJob(
                job_id=job_id,
                out_path=out_png,
                w=w,
                h=h,
                pixels=pixels,
                fmt="BGRA",
            )
        ):
            # queue full -> drop frame
            return

    def _write_video_manifest(self, base_dir: Path):
        if not self._video_manifest:
            return
        path = base_dir / "manifest.json"
        path.write_text(
            json.dumps(asdict(self._video_manifest), indent=2),
            encoding="utf-8",
        )
