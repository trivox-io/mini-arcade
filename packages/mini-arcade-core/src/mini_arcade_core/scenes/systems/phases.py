"""
Shared system phase constants for deterministic pipeline grouping.
"""

from __future__ import annotations

from enum import IntEnum


class SystemPhase(IntEnum):
    """
    High-level execution buckets for scene systems.

    Keep values spaced to leave room for future insertions without churn.
    """

    INPUT = 10
    CONTROL = 20
    SIMULATION = 30
    PRESENTATION = 40
    RENDERING = 50
