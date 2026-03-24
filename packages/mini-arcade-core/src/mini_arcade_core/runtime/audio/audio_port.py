"""
Service interfaces for runtime components.
"""

from __future__ import annotations


class AudioPort:
    """Interface for audio playback operations."""

    def load_sound(self, sound_id: str, file_path: str):
        """
        Load a sound from a file and associate it with an identifier.

        :param sound_id: Identifier to associate with the sound.
        :type sound_id: str

        :param file_path: Path to the sound file.
        :type file_path: str
        """

    def play(self, sound_id: str, loops: int = 0):
        """
        Play the specified sound.

        :param sound_id: Identifier of the sound to play.
        :type sound_id: str

        :param loops: Number of times to loop the sound.
            0 = play once, -1 = infinite loop, 1 = play twice, etc.
        :type loops: int
        """

    def set_master_volume(self, volume: int):
        """
        Set the global audio volume.

        :param volume: Volume level in the backend's native 0-128 range.
        :type volume: int
        """

    def set_sound_volume(self, sound_id: str, volume: int):
        """
        Set the volume for one loaded sound.

        :param sound_id: Identifier of the sound to update.
        :type sound_id: str

        :param volume: Volume level in the backend's native 0-128 range.
        :type volume: int
        """
