"""
Backend module for rendering and input abstraction.
Defines the Backend interface and related types.
This is the only part of the code that talks to SDL/pygame directly.
"""

from __future__ import annotations

from .backend import (
    AudioProtocol,
    Backend,
    CaptureProtocol,
    InputProtocol,
    RenderProtocol,
    TextProtocol,
    WindowProtocol,
)

__all__ = [
    "AudioProtocol",
    "Backend",
    "CaptureProtocol",
    "InputProtocol",
    "RenderProtocol",
    "TextProtocol",
    "WindowProtocol",
]
