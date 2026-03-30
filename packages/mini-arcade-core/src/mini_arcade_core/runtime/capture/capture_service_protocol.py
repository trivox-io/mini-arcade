"""
Capture service protocol
"""

from __future__ import annotations

from pathlib import Path

from mini_arcade_core.backend import Backend
from mini_arcade_core.runtime.capture.capture_settings import CaptureSettings
from mini_arcade_core.runtime.capture.replay import (
    ReplayPlayer,
    ReplayRecorder,
)
from mini_arcade_core.runtime.capture.replay_format import ReplayHeader
from mini_arcade_core.runtime.capture.screenshot_capturer import (
    ScreenshotCapturer,
)
from mini_arcade_core.runtime.capture.video_session import VideoSession
from mini_arcade_core.runtime.input_frame import InputFrame


class CaptureServicePort:
    """
    Interface for the Capture Service.
    """

    backend: Backend
    settings: CaptureSettings
    screenshots: ScreenshotCapturer
    replay_recorder: ReplayRecorder
    replay_player: ReplayPlayer

    # -------- screenshots --------
    def screenshot(self, label: str | None = None) -> str:
        """
        Take a screenshot with an optional label.

        :param label: Optional label for the screenshot.
        :type label: str | None
        :return: Path to the saved screenshot.
        :rtype: str
        """

    def screenshot_sim(
        self, run_id: str, frame_index: int, label: str = "frame"
    ) -> str:
        """
        Take a screenshot for a simulation frame.

        :param run_id: Unique identifier for the simulation run.
        :type run_id: str

        :param frame_index: Index of the frame in the simulation.
        :type frame_index: int

        :param label: Label for the screenshot.
        :type label: str

        :return: Path to the saved screenshot.
        :rtype: str
        """

    # -------- replays --------
    @property
    def replay_playing(self) -> bool:
        """
        Check if a replay is currently being played back.

        :return: True if a replay is active, False otherwise.
        :rtype: bool
        """

    @property
    def replay_recording(self) -> bool:
        """
        Check if a replay is currently being recorded.

        :return: True if recording is active, False otherwise.
        :rtype: bool
        """

    def start_replay_record(
        self,
        *,
        filename: str,
        header: ReplayHeader,
    ):
        """
        Start recording a replay.

        :param filename: The filename to save the replay to.
        :type filename: str
        :param header: The header information for the replay.
        :type header: ReplayHeader
        """

    def stop_replay_record(self):
        """Stop recording the current replay."""

    def record_input(self, frame: InputFrame):
        """
        Record an input frame to the replay.

        :param frame: The input frame to record.
        :type frame: InputFrame
        """

    def start_replay_play(self, filename: str) -> ReplayHeader:
        """
        Start playing back a replay.

        :param filename: The filename of the replay to play.
        :type filename: str
        :return: The header information of the replay.
        :rtype: ReplayHeader
        """

    def stop_replay_play(self):
        """Stop playing back the current replay."""

    def next_replay_input(self) -> InputFrame:
        """
        Get the next input frame from the replay.

        :return: The next input frame.
        :rtype: InputFrame
        """

    @property
    def video_recording(self) -> bool:
        """
        Check if video recording is currently active.

        :return: True if video recording is active, False otherwise.
        :rtype: bool
        """

    @property
    def video_busy(self) -> bool:
        """
        Check if video capture is recording or still finalizing/encoding.

        :return: True if the capture pipeline is busy, False otherwise.
        :rtype: bool
        """

    @property
    def current_video_session(self) -> VideoSession | None:
        """
        Current human-facing video session metadata, if any.

        :return: Current session metadata or None.
        :rtype: VideoSession | None
        """

    def start_video_record(
        self,
        *,
        fps: int = 60,
        capture_fps: int = 60,
        label: str | None = None,
        scene_id: str | None = None,
    ) -> Path:
        """
        Start recording video.

        :param fps: Frames per second for the output video.
        :type fps: int
        :param capture_fps: Frames per second to capture from the engine.
        :type capture_fps: int
        :param label: Optional human-friendly label for the session folder.
        :type label: str | None
        :param scene_id: Optional scene id associated with the recording start.
        :type scene_id: str | None
        :return: Path to the directory where video frames are saved.
        :rtype: Path
        """

    def stop_video_record(self):
        """Stop recording video."""

    def handle_quit_request(self) -> bool:
        """
        Handle a user quit request while video capture may be active.

        :return: True if the engine may quit immediately, False otherwise.
        :rtype: bool
        """

    def begin_video_frame(self, *, dt: float) -> None:
        """
        Advance the recording timeline to the current frame before scene logic runs.

        :param dt: Real elapsed frame delta time in seconds.
        :type dt: float
        """

    def record_video_frame(self, *, frame_index: int, dt: float):
        """
        Call this once per engine frame (from EngineRunner) AFTER render.

        :param frame_index: The index of the current frame.
        :type frame_index: int
        :param dt: Real elapsed frame delta time in seconds.
        :type dt: float
        """
