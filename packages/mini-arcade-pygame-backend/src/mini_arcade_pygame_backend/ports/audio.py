"""
Audio port for the Mini Arcade pygame backend.
"""

from __future__ import annotations

import pygame
from mini_arcade_core.backend.utils import (  # pyright: ignore[reportMissingImports]
    validate_file_exists,
)


class AudioPort:
    """
    Audio port for the Mini Arcade pygame backend.
    """

    def __init__(self):
        self._sounds: dict[str, pygame.mixer.Sound] = {}

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
        pygame.mixer.init(
            frequency=int(frequency),
            channels=int(channels),
            buffer=int(chunk_size),
        )

    def shutdown(self):
        """Shutdown the audio subsystem."""
        pygame.mixer.quit()

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
        p = validate_file_exists(path)
        self._sounds[sound_id] = pygame.mixer.Sound(p)

    def play_sound(self, sound_id: str, loops: int = 0):
        """
        Play a loaded sound.

        :param sound_id: The identifier for the sound.
        :type sound_id: str
        :param loops: The number of times to loop the sound (default: 0).
        :type loops: int
        """
        s = self._sounds.get(sound_id)
        if s:
            s.play(loops=int(loops))

    def set_master_volume(self, volume: int):
        """
        Set the master volume.

        :param volume: The master volume (0-100).
        :type volume: int
        """
        v = max(0, min(128, int(volume))) / 128.0
        pygame.mixer.music.set_volume(v)
        for s in self._sounds.values():
            s.set_volume(v)

    def set_sound_volume(self, sound_id: str, volume: int):
        """
        Set the volume for a specific sound.

        :param sound_id: The identifier for the sound.
        :type sound_id: str
        :param volume: The volume for the sound (0-100).
        :type volume: int
        """
        s = self._sounds.get(sound_id)
        if not s:
            return
        v = max(0, min(128, int(volume))) / 128.0
        s.set_volume(v)

    def stop_all(self):
        """Stop all currently playing sounds."""
        pygame.mixer.stop()
