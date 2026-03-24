"""
Capture service managing screenshots, replay, and video recording.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import asdict
from pathlib import Path
from typing import Optional, Union
from uuid import uuid4

from mini_arcade_core.backend import Backend
from mini_arcade_core.bus import event_bus
from mini_arcade_core.runtime.capture import events as capture_events
from mini_arcade_core.runtime.capture.capture_service_protocol import (
    CaptureServicePort,
)
from mini_arcade_core.runtime.capture.capture_settings import CaptureSettings
from mini_arcade_core.runtime.capture.capture_worker import (
    CaptureJob,
    CaptureResult,
)
from mini_arcade_core.runtime.capture.encode_worker import (
    EncodeJob,
    EncodeResult,
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

VideoStartHook = Callable[[Path, str, int, int], None]
VideoFinalizeHook = Callable[[Path, VideoManifest, Union[str, None]], None]


# pylint: disable=too-many-instance-attributes
class CaptureService(CaptureServicePort):
    """
    Owns:
        - screenshots (delegated)
        - replay recording (InputFrame stream)
        - replay playback (feeds InputFrames)
        - video recording + optional encode
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
        self._video_elapsed_seconds: float = 0.0
        self._video_last_frame_index: int | None = None
        self.encoder = EncodeWorker()
        self.on_video_start: VideoStartHook | None = None
        self.on_video_finalize: VideoFinalizeHook | None = None

        # Emit completion events when worker jobs finish.
        self.screenshots.worker.set_on_done(self._on_capture_done)
        self.encoder.set_on_done(self._on_encode_done)
        self.encoder.start()

    # -------- screenshots --------
    def screenshot(self, label: str | None = None) -> str:
        out = self.screenshots.screenshot(label)
        event_bus.emit(
            capture_events.SCREENSHOT_QUEUED,
            path=out,
            label=label,
        )
        return out

    def screenshot_sim(
        self, run_id: str, frame_index: int, label: str = "frame"
    ) -> str:
        out = self.screenshots.screenshot_sim(run_id, frame_index, label)
        event_bus.emit(
            capture_events.SCREENSHOT_QUEUED,
            path=out,
            label=label,
            run_id=run_id,
            frame_index=frame_index,
        )
        return out

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
        event_bus.emit(capture_events.REPLAY_RECORD_STARTED, path=str(path))

    def stop_replay_record(self):
        path: str | None = None
        writer = getattr(self.replay_recorder, "_writer", None)
        if writer is not None:
            writer_path = getattr(writer, "path", None)
            if writer_path is not None:
                path = str(writer_path)
        self.replay_recorder.stop()
        event_bus.emit(capture_events.REPLAY_RECORD_STOPPED, path=path)

    def record_input(self, frame: InputFrame):
        self.replay_recorder.record(frame)

    def start_replay_play(self, filename: str) -> ReplayHeader:
        path = Path(self.settings.replays_dir) / filename
        header = self.replay_player.start(path)
        event_bus.emit(capture_events.REPLAY_PLAY_STARTED, path=str(path))
        return header

    def stop_replay_play(self):
        self.replay_player.stop()
        event_bus.emit(capture_events.REPLAY_PLAY_STOPPED)

    def next_replay_input(self) -> InputFrame:
        try:
            return self.replay_player.next()
        except RuntimeError as exc:
            if "Replay finished" not in str(exc):
                raise
            event_bus.emit(capture_events.REPLAY_PLAY_FINISHED)
            return InputFrame(frame_index=0, dt=0.0)

    # -------- video --------

    @property
    def video_recording(self) -> bool:
        return self.video.active

    @property
    def current_video_time_seconds(self) -> float:
        """
        Return the current elapsed video recording time in seconds, based on frame indices
        and configured FPS. This is more accurate than wall clock time for determining video
        timestamps, especially if frames are dropped or if the game experiences lag.

        :return: Elapsed video recording time in seconds.
        :rtype: float
        """
        return float(self._video_elapsed_seconds)

    def start_video_record(
        self, *, fps: int = 60, capture_fps: int = 15
    ) -> Path:
        self.video.cfg.fps = fps
        self.video.cfg.capture_fps = capture_fps
        self._video_elapsed_seconds = 0.0
        self._video_last_frame_index = None

        base_dir = self.video.start()
        self._video_manifest = VideoManifest(
            run_id=self.video.run_id,
            fps=fps,
            capture_fps=capture_fps,
            frames=0,
        )
        self._write_video_manifest(base_dir)
        if self.on_video_start is not None:
            try:
                self.on_video_start(
                    base_dir,
                    self.video.run_id,
                    fps,
                    capture_fps,
                )
            except Exception:  # pylint: disable=broad-exception-caught
                logger.exception("[capture] on_video_start hook failed")
        event_bus.emit(capture_events.VIDEO_STARTED, path=str(base_dir))
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

        if self.on_video_finalize is not None:
            try:
                self.on_video_finalize(
                    base_dir,
                    manifest,
                    self.settings.ffmpeg_path,
                )
            except Exception:  # pylint: disable=broad-exception-caught
                logger.exception("[capture] on_video_finalize hook failed")

        out_mp4: Path | None = None
        encode_queued = False
        if self.settings.encode_on_stop:
            out_mp4 = base_dir / "video.mp4"
            audio_path = base_dir / "audio.wav"
            job = EncodeJob(
                job_id=f"encode:{uuid4().hex}",
                ffmpeg_path=self.settings.ffmpeg_path,
                frames_dir=base_dir,
                output_path=out_mp4,
                audio_path=audio_path if audio_path.is_file() else None,
                input_fps=manifest.capture_fps,
                output_fps=manifest.fps,
                codec=self.settings.video_codec,
                crf=self.settings.video_crf,
                preset=self.settings.video_preset,
                keep_frames=self.settings.keep_frames,
            )
            encode_queued = self.encoder.enqueue(job)
            if not encode_queued:
                logger.warning("[encode] dropped encode job (queue full)")
            else:
                logger.info(f"[encode] queued -> {out_mp4}")

        if encode_queued and out_mp4 is not None:
            event_bus.emit(
                capture_events.VIDEO_ENCODE_QUEUED,
                path=str(out_mp4),
            )

        self.video.stop()
        self._video_manifest = None
        self._video_last_frame_index = None
        logger.info("Video recording stopped.")
        event_bus.emit(capture_events.VIDEO_STOPPED, path=str(base_dir))

    def record_video_frame(self, *, frame_index: int):
        """
        Call this once per engine frame (from EngineRunner) AFTER render.
        """
        if not self.video.active:
            return
        if self._video_last_frame_index is None:
            self._video_last_frame_index = int(frame_index)
        else:
            delta_frames = max(
                0,
                int(frame_index) - int(self._video_last_frame_index),
            )
            self._video_elapsed_seconds += float(delta_frames) / float(
                max(1, int(self.video.cfg.fps))
            )
            self._video_last_frame_index = int(frame_index)
        if not self.video.should_capture(frame_index):
            return

        worker = self.screenshots.worker

        # Backpressure: if worker is overloaded, drop to protect gameplay.
        if hasattr(worker, "qsize") and worker.qsize() > 200:
            return

        out_png, out_frame = self.video.next_paths()
        out_png.parent.mkdir(parents=True, exist_ok=True)

        # Capture bytes (no disk I/O on the main thread).
        w, h, pixels = self.backend.capture.argb8888_bytes()

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

    def _on_capture_done(self, result: CaptureResult) -> None:
        # Video recording frames share the capture worker; avoid spamming
        # screenshot completion events for each encoded frame.
        if result.job_id.startswith("video:"):
            return
        if result.ok:
            event_bus.emit(
                capture_events.SCREENSHOT_DONE,
                path=str(result.out_path),
                job_id=result.job_id,
            )
            return
        event_bus.emit(
            capture_events.SCREENSHOT_FAILED,
            path=str(result.out_path),
            job_id=result.job_id,
            error=result.error or "Unknown screenshot error",
        )

    def _on_encode_done(self, result: EncodeResult) -> None:
        if result.ok:
            event_bus.emit(
                capture_events.VIDEO_ENCODE_DONE,
                path=str(result.output_path) if result.output_path else None,
                job_id=result.job_id,
            )
            return
        event_bus.emit(
            capture_events.VIDEO_ENCODE_FAILED,
            job_id=result.job_id,
            error=result.error or "Unknown encode error",
        )
