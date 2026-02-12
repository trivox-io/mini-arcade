"""
Replay recording and playback functionality.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional

from mini_arcade_core.runtime.capture.replay_format import (
    ReplayHeader,
    ReplayReader,
    ReplayWriter,
)
from mini_arcade_core.runtime.input_frame import InputFrame


@dataclass
class ReplayRecorderConfig:
    """
    Configuration for replay recording.

    :ivar path (Path): Path to save the replay file.
    :ivar header (ReplayHeader): Header information for the replay.
    """

    path: Path
    header: ReplayHeader


class ReplayRecorder:
    """Recorder for game replays."""

    def __init__(self):
        self._writer: Optional[ReplayWriter] = None

    @property
    def active(self) -> bool:
        """
        Check if the recorder is currently active.

        :return: True if recording is active, False otherwise.
        :rtype: bool
        """
        return self._writer is not None

    def start(self, cfg: ReplayRecorderConfig) -> None:
        """
        Start recording a replay.

        :param cfg: Configuration for the replay recorder.
        :type cfg: ReplayRecorderConfig
        """
        if self._writer:
            raise RuntimeError("ReplayRecorder already active")
        self._writer = ReplayWriter(cfg.path, cfg.header)
        self._writer.open()

    def record(self, frame: InputFrame) -> None:
        """
        Record an input frame to the replay.

        :param frame: The input frame to record.
        :type frame: InputFrame
        """
        if self._writer:
            self._writer.write_frame(frame)

    def stop(self) -> None:
        """Stop recording the current replay."""
        if self._writer:
            self._writer.close()
            self._writer = None


class ReplayPlayer:
    """Player for game replays."""

    def __init__(self):
        self._reader: Optional[ReplayReader] = None
        self._it: Optional[Iterator[InputFrame]] = None
        self.header: Optional[ReplayHeader] = None

    @property
    def active(self) -> bool:
        """
        Check if the player is currently active.

        :return: True if a replay is being played, False otherwise.
        :rtype: bool
        """
        return self._it is not None

    def start(self, path: Path) -> ReplayHeader:
        """
        Start playing back a replay.

        :param path: Path to the replay file.
        :type path: Path
        :return: The header information of the replay.
        :rtype: ReplayHeader
        """
        if self._reader:
            raise RuntimeError("ReplayPlayer already active")
        self._reader = ReplayReader(path)
        self.header = self._reader.open()
        self._it = self._reader.frames()
        return self.header

    def next(self) -> InputFrame:
        """
        Get the next input frame from the replay.

        :return: The next input frame.
        :rtype: InputFrame
        """
        if not self._it:
            raise RuntimeError("ReplayPlayer not active")
        try:
            return next(self._it)
        except StopIteration as exc:
            self.stop()
            raise RuntimeError("Replay finished") from exc

    def stop(self) -> None:
        """Stop playing back the current replay."""
        if self._reader:
            self._reader.close()
        self._reader = None
        self._it = None
        self.header = None
