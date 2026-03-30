"""
Capture video session state models.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class VideoSession:
    """
    Human-facing capture session metadata.
    """

    run_id: str
    label: str
    scene_id: str
    started_at_iso: str
    state: str
    message: str
    base_dir: Path
    frames_dir: Path
    output_path: Path | None = None
    progress: float = 0.0
