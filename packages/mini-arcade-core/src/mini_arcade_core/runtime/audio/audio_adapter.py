"""
Module providing runtime adapters for window and scene management.
"""

from __future__ import annotations

from mini_arcade_core.backend import Backend
from mini_arcade_core.runtime.audio.audio_port import AudioPort


class SDLAudioAdapter(AudioPort):
    """Runtime audio adapter that forwards to the active backend."""

    def __init__(self, backend: Backend):
        self.backend = backend

    def load_sound(self, sound_id: str, file_path: str):
        self.backend.audio.load_sound(sound_id, file_path)

    def play(self, sound_id: str, loops: int = 0):
        self.backend.audio.play_sound(sound_id, loops)

    def set_master_volume(self, volume: int):
        self.backend.audio.set_master_volume(volume)

    def set_sound_volume(self, sound_id: str, volume: int):
        self.backend.audio.set_sound_volume(sound_id, volume)

    def stop_all(self):
        self.backend.audio.stop_all()
