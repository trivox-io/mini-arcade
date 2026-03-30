"""
Capture service managing screenshots, replay, and video recording.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from threading import Thread
from typing import Optional
from uuid import uuid4
import re
from time import monotonic

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
    EncodeProgress,
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
from mini_arcade_core.runtime.capture.video_session import VideoSession
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.utils import logger

VideoStartHook = Callable[..., None]
VideoFinalizeHook = Callable[..., None]


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
        self.video = VideoRecorder(VideoRecordConfig(fps=60, capture_fps=60))
        self._video_manifest: Optional[VideoManifest] = None
        self._video_session: VideoSession | None = None
        self._video_elapsed_seconds: float = 0.0
        self._video_frame_target_seconds: float = 0.0
        self._video_frame_times_seconds: list[float] = []
        self._video_last_frame_index: int | None = None
        self._encode_started_at_seconds: float | None = None
        self._finalize_thread: Thread | None = None
        self.encoder = EncodeWorker()
        self.on_video_start: VideoStartHook | None = None
        self.on_video_finalize: VideoFinalizeHook | None = None

        # Emit completion events when worker jobs finish.
        self.screenshots.worker.set_on_done(self._on_capture_done)
        self.encoder.set_on_done(self._on_encode_done)
        self.encoder.set_on_progress(self._on_encode_progress)
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
    def video_busy(self) -> bool:
        session = self._video_session
        if session is None:
            return False
        return session.state in {"recording", "finalizing", "encoding"}

    @property
    def current_video_session(self) -> VideoSession | None:
        return self._video_session

    @property
    def current_video_time_seconds(self) -> float:
        """
        Return the current elapsed video recording time in seconds, based on frame indices
        and configured FPS. This is more accurate than wall clock time for determining video
        timestamps, especially if frames are dropped or if the game experiences lag.

        :return: Elapsed video recording time in seconds.
        :rtype: float
        """
        if self.video.active:
            return float(
                max(
                    float(self._video_elapsed_seconds),
                    float(self._video_frame_target_seconds),
                )
            )
        return float(self._video_elapsed_seconds)

    def begin_video_frame(self, *, dt: float) -> None:
        """
        Advance the capture timeline to the current frame before scene logic runs.
        """
        if not self.video.active:
            return
        self._video_frame_target_seconds = (
            float(self._video_elapsed_seconds) + max(0.0, float(dt))
        )

    def start_video_record(
        self,
        *,
        fps: int = 60,
        capture_fps: int = 60,
        label: str | None = None,
        scene_id: str | None = None,
    ) -> Path:
        if self.video_busy:
            session = self._video_session
            logger.warning(
                "[capture] start_video_record ignored while video pipeline is busy"
            )
            if session is not None:
                return session.base_dir
            return Path(self.settings.recordings_dir)
        self.video.cfg.fps = fps
        self.video.cfg.capture_fps = capture_fps
        self._video_elapsed_seconds = 0.0
        self._video_frame_target_seconds = 0.0
        self._video_frame_times_seconds = []
        self._video_last_frame_index = None
        self._encode_started_at_seconds = None

        recording_label = str(label or scene_id or "capture").strip() or "capture"
        recording_scene_id = str(scene_id or "unknown").strip() or "unknown"

        base_dir = self.video.start(
            out_dir=Path(self.settings.recordings_dir),
            label=recording_label,
        )
        self._video_manifest = VideoManifest(
            run_id=self.video.run_id,
            fps=fps,
            capture_fps=float(capture_fps),
            frames=0,
            duration_seconds=0.0,
            effective_capture_fps=float(capture_fps),
        )
        frames_dir = self.video.frames_dir_path or (base_dir / "raw" / "frames")
        self._video_session = VideoSession(
            run_id=self.video.run_id,
            label=recording_label,
            scene_id=recording_scene_id,
            started_at_iso=datetime.now().isoformat(timespec="seconds"),
            state="recording",
            message="Recording in progress.",
            base_dir=base_dir,
            frames_dir=frames_dir,
            output_path=base_dir / "video.mp4",
            progress=0.0,
        )
        self._write_video_manifest(base_dir)
        self._write_video_session()
        self._emit_video_state_changed()
        if self.on_video_start is not None:
            try:
                self.on_video_start(
                    base_dir=base_dir,
                    run_id=self.video.run_id,
                    fps=fps,
                    capture_fps=capture_fps,
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
        frames_dir = self.video.frames_dir_path or (base_dir / "raw" / "frames")
        frame_times_seconds = tuple(self._video_frame_times_seconds)
        duration_seconds = float(self._video_elapsed_seconds)
        self._set_video_session_state(
            "finalizing",
            "Finishing recording in background.",
        )
        self._write_video_manifest(base_dir)
        logger.info(f"Video frames saved to: {base_dir}")
        event_bus.emit(capture_events.VIDEO_FINALIZING, path=str(base_dir))

        self.video.stop()
        self._video_manifest = None
        self._video_last_frame_index = None
        self._video_frame_target_seconds = 0.0
        self._video_frame_times_seconds = []
        self._video_elapsed_seconds = 0.0
        self._finalize_thread = Thread(
            target=self._finalize_video_recording,
            kwargs={
                "base_dir": base_dir,
                "manifest": manifest,
                "frames_dir": frames_dir,
                "frame_times_seconds": frame_times_seconds,
                "duration_seconds": duration_seconds,
            },
            name=f"capture-finalize-{manifest.run_id}",
            daemon=True,
        )
        self._finalize_thread.start()
        logger.info("Video recording stopped.")
        event_bus.emit(capture_events.VIDEO_STOPPED, path=str(base_dir))

    def handle_quit_request(self) -> bool:
        session = self._video_session
        if session is None:
            return True

        if self.video_recording:
            self.stop_video_record()
            session = self._video_session
            message = (
                session.message
                if session is not None
                else "Finishing recording. Please wait."
            )
            event_bus.emit(
                capture_events.VIDEO_QUIT_BLOCKED,
                message=message,
                state="recording",
            )
            return False

        if self.video_busy:
            message = (
                session.message
                if session is not None
                else "Encoding video. Please wait."
            )
            self._set_video_session_state(
                session.state if session is not None else "encoding",
                message,
            )
            event_bus.emit(
                capture_events.VIDEO_QUIT_BLOCKED,
                message=message,
                state=session.state if session is not None else "encoding",
            )
            return False

        return True

    def record_video_frame(self, *, frame_index: int, dt: float):
        """
        Call this once per engine frame (from EngineRunner) AFTER render.
        """
        if not self.video.active:
            return
        self._video_elapsed_seconds = max(
            float(self._video_elapsed_seconds),
            float(self._video_frame_target_seconds),
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
            self.video.rollback_last_frame()
            return

        if self._video_manifest:
            self._video_frame_times_seconds.append(
                float(self._video_elapsed_seconds)
            )
            self._video_manifest = VideoManifest(
                run_id=self._video_manifest.run_id,
                fps=self._video_manifest.fps,
                capture_fps=self._video_manifest.capture_fps,
                frames=out_frame + 1,
                duration_seconds=self._video_manifest.duration_seconds,
                effective_capture_fps=self._video_manifest.effective_capture_fps,
            )
            self._refresh_video_manifest_stats()
            if self.video.base_dir is not None:
                self._write_video_manifest(self.video.base_dir)

    def _write_video_manifest(self, base_dir: Path):
        if not self._video_manifest:
            return
        self._write_video_manifest_payload(base_dir, self._video_manifest)

    def _write_video_manifest_payload(
        self,
        base_dir: Path,
        manifest: VideoManifest,
    ) -> None:
        path = self._manifests_dir(base_dir) / "manifest.json"
        path.write_text(json.dumps(asdict(manifest), indent=2), encoding="utf-8")

    def _write_frame_times(self, base_dir: Path) -> None:
        self._write_frame_times_payload(base_dir, self._video_frame_times_seconds)

    def _write_frame_times_payload(
        self,
        base_dir: Path,
        frame_times_seconds: list[float] | tuple[float, ...],
    ) -> None:
        path = self._manifests_dir(base_dir) / "frame_times.json"
        path.write_text(
            json.dumps(
                [float(value) for value in frame_times_seconds],
                indent=2,
            ),
            encoding="utf-8",
        )

    def _refresh_video_manifest_stats(self) -> None:
        manifest = self._video_manifest
        if manifest is None:
            return
        duration_seconds = max(0.0, float(self._video_elapsed_seconds))
        effective_capture_fps = (
            float(manifest.frames) / duration_seconds
            if duration_seconds > 0.0 and manifest.frames > 0
            else float(manifest.capture_fps)
        )
        self._video_manifest = VideoManifest(
            run_id=manifest.run_id,
            fps=manifest.fps,
            capture_fps=manifest.capture_fps,
            frames=manifest.frames,
            duration_seconds=duration_seconds,
            effective_capture_fps=effective_capture_fps,
        )

    @staticmethod
    def _normalize_frame_sequence(frames_dir: Path) -> int:
        """
        Ensure captured frame filenames are contiguous before encoding.

        This prevents ffmpeg's numbered-sequence reader from truncating output
        at the first missing frame if the capture queue dropped any frame jobs.
        """
        if not frames_dir.is_dir():
            return 0

        pattern = re.compile(r"^frame_(\d+)\.png$")
        frames = sorted(
            (
                path
                for path in frames_dir.glob("frame_*.png")
                if pattern.match(path.name)
            ),
            key=lambda path: int(pattern.match(path.name).group(1)),
        )
        if not frames:
            return 0

        expected_names = [
            frames_dir / f"frame_{index:08d}.png"
            for index in range(len(frames))
        ]
        if all(path == expected for path, expected in zip(frames, expected_names)):
            return len(frames)

        temp_paths: list[Path] = []
        for index, path in enumerate(frames):
            temp_path = frames_dir / f"__normalize_{index:08d}.png"
            path.rename(temp_path)
            temp_paths.append(temp_path)

        for index, temp_path in enumerate(temp_paths):
            final_path = frames_dir / f"frame_{index:08d}.png"
            temp_path.rename(final_path)

        return len(temp_paths)

    def _write_video_session(self) -> None:
        session = self._video_session
        if session is None:
            return

        payload = {
            "run_id": session.run_id,
            "label": session.label,
            "scene_id": session.scene_id,
            "started_at_iso": session.started_at_iso,
            "state": session.state,
            "message": session.message,
            "base_dir": str(session.base_dir),
            "frames_dir": str(session.frames_dir),
            "output_path": (
                str(session.output_path) if session.output_path else None
            ),
            "progress": float(session.progress),
        }
        path = self._manifests_dir(session.base_dir) / "session.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _set_video_session_state(
        self,
        state: str,
        message: str,
        *,
        output_path: Path | None = None,
        progress: float | None = None,
    ) -> None:
        session = self._video_session
        if session is None:
            return
        self._video_session = VideoSession(
            run_id=session.run_id,
            label=session.label,
            scene_id=session.scene_id,
            started_at_iso=session.started_at_iso,
            state=state,
            message=message,
            base_dir=session.base_dir,
            frames_dir=session.frames_dir,
            output_path=output_path if output_path is not None else session.output_path,
            progress=(
                max(0.0, min(1.0, float(progress)))
                if progress is not None
                else session.progress
            ),
        )
        self._write_video_session()
        self._emit_video_state_changed()

    def _set_video_session_progress(
        self,
        progress: float,
        *,
        message: str | None = None,
    ) -> None:
        session = self._video_session
        if session is None:
            return
        self._video_session = VideoSession(
            run_id=session.run_id,
            label=session.label,
            scene_id=session.scene_id,
            started_at_iso=session.started_at_iso,
            state=session.state,
            message=message if message is not None else session.message,
            base_dir=session.base_dir,
            frames_dir=session.frames_dir,
            output_path=session.output_path,
            progress=max(0.0, min(1.0, float(progress))),
        )
        self._write_video_session()

    def _emit_video_state_changed(self) -> None:
        session = self._video_session
        if session is None:
            return
        event_bus.emit(
            capture_events.VIDEO_STATE_CHANGED,
            run_id=session.run_id,
            state=session.state,
            message=session.message,
            path=str(session.output_path or session.base_dir),
            progress=float(session.progress),
        )

    @staticmethod
    def _manifests_dir(base_dir: Path) -> Path:
        path = Path(base_dir) / "raw" / "manifests"
        path.mkdir(parents=True, exist_ok=True)
        return path

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

    def _finalize_video_recording(
        self,
        *,
        base_dir: Path,
        manifest: VideoManifest,
        frames_dir: Path,
        frame_times_seconds: tuple[float, ...],
        duration_seconds: float,
    ) -> None:
        try:
            capture_worker = self.screenshots.worker
            if hasattr(capture_worker, "wait_until_idle"):
                capture_worker.wait_until_idle()

            actual_frames = self._normalize_frame_sequence(frames_dir)
            normalized_frame_times = list(frame_times_seconds[:actual_frames])
            finalized_manifest = VideoManifest(
                run_id=manifest.run_id,
                fps=manifest.fps,
                capture_fps=manifest.capture_fps,
                frames=actual_frames,
                duration_seconds=max(0.0, float(duration_seconds)),
                effective_capture_fps=(
                    float(actual_frames) / float(duration_seconds)
                    if duration_seconds > 0.0 and actual_frames > 0
                    else float(manifest.capture_fps)
                ),
            )
            self._write_frame_times_payload(base_dir, normalized_frame_times)
            self._write_video_manifest_payload(base_dir, finalized_manifest)

            if self.on_video_finalize is not None:
                try:
                    self.on_video_finalize(
                        base_dir=base_dir,
                        manifest=finalized_manifest,
                        ffmpeg_path=self.settings.ffmpeg_path,
                    )
                except Exception:  # pylint: disable=broad-exception-caught
                    logger.exception("[capture] on_video_finalize hook failed")

            out_mp4: Path | None = None
            encode_queued = False
            if self.settings.encode_on_stop:
                out_mp4 = base_dir / "video.mp4"
                audio_path = base_dir / "raw" / "audio" / "audio.wav"
                job = EncodeJob(
                    job_id=f"encode:{uuid4().hex}",
                    ffmpeg_path=self.settings.ffmpeg_path,
                    frames_dir=frames_dir,
                    output_path=out_mp4,
                    audio_path=audio_path if audio_path.is_file() else None,
                    input_fps=max(
                        1.0, float(finalized_manifest.effective_capture_fps)
                    ),
                    output_fps=finalized_manifest.fps,
                    codec=self.settings.video_codec,
                    crf=self.settings.video_crf,
                    preset=self.settings.video_preset,
                    keep_frames=self.settings.keep_frames,
                    video_interpolate=bool(self.settings.video_interpolate),
                    expected_duration_seconds=float(
                        finalized_manifest.duration_seconds
                    ),
                    frame_times_seconds=tuple(normalized_frame_times),
                )
                encode_queued = self.encoder.enqueue(job)
                if not encode_queued:
                    logger.warning("[encode] dropped encode job (queue full)")
                else:
                    logger.info(f"[encode] queued -> {out_mp4}")
                    self._set_video_session_state(
                        "encoding",
                        "Encoding video. Please wait.",
                        output_path=out_mp4,
                        progress=0.0,
                    )
                    self._encode_started_at_seconds = monotonic()
                    event_bus.emit(
                        capture_events.VIDEO_ENCODE_STARTED,
                        path=str(out_mp4),
                    )

            if encode_queued and out_mp4 is not None:
                event_bus.emit(
                    capture_events.VIDEO_ENCODE_QUEUED,
                    path=str(out_mp4),
                )
            elif out_mp4 is not None:
                self._set_video_session_state(
                    "failed",
                    "Recording finished, but encoding could not be queued.",
                    output_path=out_mp4,
                )
            else:
                self._set_video_session_state(
                    "completed",
                    "Recording saved.",
                )
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("[capture] background finalization failed")
            self._set_video_session_state(
                "failed",
                "Recording finalization failed.",
            )
        finally:
            self._finalize_thread = None

    def _on_encode_done(self, result: EncodeResult) -> None:
        self._encode_started_at_seconds = None
        if result.ok:
            self._set_video_session_state(
                "completed",
                "Video ready.",
                output_path=result.output_path,
                progress=1.0,
            )
            event_bus.emit(
                capture_events.VIDEO_ENCODE_DONE,
                path=str(result.output_path) if result.output_path else None,
                job_id=result.job_id,
            )
            return
        self._set_video_session_state(
            "failed",
            result.error or "Video encode failed.",
        )
        event_bus.emit(
            capture_events.VIDEO_ENCODE_FAILED,
            job_id=result.job_id,
            error=result.error or "Unknown encode error",
        )

    def _on_encode_progress(self, result: EncodeProgress) -> None:
        session = self._video_session
        if session is None or session.state != "encoding":
            return
        percent = int(round(max(0.0, min(1.0, float(result.progress))) * 100.0))
        eta_text = ""
        if (
            self._encode_started_at_seconds is not None
            and float(result.progress) > 0.0001
        ):
            elapsed = max(0.0, monotonic() - self._encode_started_at_seconds)
            eta_seconds = max(
                0.0,
                (elapsed / float(result.progress)) - elapsed,
            )
            eta_text = f" | ETA {int(round(eta_seconds))}s"
        self._set_video_session_progress(
            result.progress,
            message=f"Encoding video... {percent}%{eta_text}",
        )
        event_bus.emit(
            capture_events.VIDEO_ENCODE_PROGRESS,
            job_id=result.job_id,
            progress=float(result.progress),
        )
