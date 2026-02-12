"""
Replay file format for mini-arcade.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterator, Optional, TextIO

from mini_arcade_core.runtime.input_frame import InputFrame

REPLAY_MAGIC = "mini-arcade-replay"
REPLAY_VERSION = 1


@dataclass(frozen=True)
class ReplayHeader:
    """
    Header information for a mini-arcade replay file.

    :ivar magic: Magic string to identify the file type.
    :ivar version: Version of the replay format.
    :ivar game_id: Identifier for the game.
    :ivar initial_scene: Name of the initial scene.
    :ivar seed: Seed used for random number generation.
    :ivar fps: Frames per second of the replay.
    """

    magic: str = REPLAY_MAGIC
    version: int = REPLAY_VERSION
    game_id: str = "unknown"
    initial_scene: str = "unknown"
    seed: int = 0
    fps: int = 60


class ReplayWriter:
    """Replay file writer."""

    def __init__(self, path: Path, header: ReplayHeader):
        """
        :param path: Path to save the replay file.
        :type path: Path
        :param header: Header information for the replay.
        :type header: ReplayHeader
        """
        self.path = path
        self.header = header
        self._f: Optional[TextIO] = None

    def open(self) -> None:
        """Open the replay file for writing."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._f = self.path.open("w", encoding="utf-8")
        self._f.write(json.dumps(asdict(self.header)) + "\n")

    def write_frame(self, frame: InputFrame) -> None:
        """
        Write an input frame to the replay file.

        :param frame: Input frame to write.
        :type frame: InputFrame
        """
        if not self._f:
            raise RuntimeError("ReplayWriter is not open")
        self._f.write(json.dumps(frame.to_dict()) + "\n")

    def close(self) -> None:
        """Close the replay file."""
        if self._f:
            self._f.close()
            self._f = None


class ReplayReader:
    """Replay file reader."""

    def __init__(self, path: Path):
        """
        :param path: Path to the replay file.
        :type path: Path"""
        self.path = path
        self.header: Optional[ReplayHeader] = None
        self._f: Optional[TextIO] = None

    def open(self) -> ReplayHeader:
        """
        Open the replay file for reading.

        :return: The replay header.
        :rtype: ReplayHeader
        """
        self._f = self.path.open("r", encoding="utf-8")
        header_line = self._f.readline()
        self.header = ReplayHeader(**json.loads(header_line))
        if self.header.magic != REPLAY_MAGIC:
            raise ValueError("Not a mini-arcade replay file")
        return self.header

    def frames(self) -> Iterator[InputFrame]:
        """
        Iterate over input frames in the replay file.

        :return: Input frames from the replay.
        :rtype: Iterator[InputFrame]
        """
        if not self._f:
            raise RuntimeError("ReplayReader is not open")
        for line in self._f:
            if not line.strip():
                continue
            yield InputFrame.from_dict(json.loads(line))

    def close(self) -> None:
        """Close the replay file."""
        if self._f:
            self._f.close()
            self._f = None
