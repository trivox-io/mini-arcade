"""
Service interfaces for runtime components.
"""

from __future__ import annotations


class FilePort:
    """Interface for file operations."""

    def write_bytes(self, path: str, data: bytes):
        """
        Write bytes to a file.

        :param path: Path to the file.
        :type path: str

        :param data: Data to write.
        :type data: bytes
        """

    def write_text(self, path: str, text: str):
        """
        Write text to a file.

        :param path: Path to the file.
        :type path: str

        :param text: Text to write.
        :type text: str
        """
