"""
Audio port for the Mini Arcade native backend.
"""

from __future__ import annotations

from mini_arcade_core.backend.utils import (  # pyright: ignore[reportMissingImports]
    validate_file_exists,
)

# Justification: native is a compiled extension module.
# pylint: disable=no-name-in-module
from mini_arcade_native_backend import _native as native  # type: ignore


class AudioPort:
    """
    Audio port for the Mini Arcade native backend.

    :param native_audio: The native audio module.
    :type native_audio: native.Audio
    """

    def __init__(self, native_audio: native.Audio):
        self._a = native_audio

    def init(
        self, frequency: int = 44100, channels: int = 2, chunk_size: int = 2048
    ):
        """
        Initialize the audio subsystem.

        :param frequency: The audio frequency (default: 44100).
        :type frequency: int
        :param channels: The number of audio channels (default: 2).
        :type channels: int
        :param chunk_size: The audio chunk size (default: 2048).
        :type chunk_size: int
        """
        self._a.init(int(frequency), int(channels), int(chunk_size))

    def shutdown(self):
        """Shutdown the audio subsystem."""
        self._a.shutdown()

    def load_sound(self, sound_id: str, path: str):
        """
        Load a sound file.

        :param sound_id: The identifier for the sound.
        :type sound_id: str
        :param path: The path to the sound file.
        :type path: str
        :raises ValueError: If sound_id is empty.
        """
        if not sound_id:
            raise ValueError("sound_id cannot be empty")
        self._a.load_sound(sound_id, validate_file_exists(path))

    def play_sound(self, sound_id: str, loops: int = 0):
        """
        Play a loaded sound.

        :param sound_id: The identifier for the sound.
        :type sound_id: str
        :param loops: The number of times to loop the sound (default: 0).
        :type loops: int
        """
        self._a.play_sound(sound_id, int(loops))

    def set_master_volume(self, volume: int):
        """
        Set the master volume.

        :param volume: The master volume (0-100).
        :type volume: int
        """
        self._a.set_master_volume(int(volume))

    def set_sound_volume(self, sound_id: str, volume: int):
        """
        Set the volume for a specific sound.

        :param sound_id: The identifier for the sound.
        :type sound_id: str
        :param volume: The volume for the sound (0-100).
        :type volume: int
        """
        self._a.set_sound_volume(sound_id, int(volume))

    def stop_all(self):
        """Stop all currently playing sounds."""
        self._a.stop_all()
