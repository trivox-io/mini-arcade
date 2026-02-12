"""
Module providing runtime adapters for window and scene management.
"""

from __future__ import annotations

from mini_arcade_core.runtime.file.file_port import FilePort


class LocalFilesAdapter(FilePort):
    """Adapter for local file operations."""

    def write_text(self, path: str, text: str):
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def write_bytes(self, path: str, data: bytes):
        with open(path, "wb") as f:
            f.write(data)
            f.write(data)
