"""
Configuration and utility functions for the mini arcade native backend.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Optional

from mini_arcade_core.backend.types import Color
from mini_arcade_core.backend.utils import rgba


@dataclass(frozen=True)
class WindowSettings:
    """
    Configuration for a game window (not implemented).

    :ivar width (int): Width of the window in pixels.
    :ivar height (int): Height of the window in pixels.
    :ivar title (str): Title of the window.
    :ivar resizable (bool): Whether the window is resizable. Default is False.
    :ivar high_dpi (bool): Whether to enable high-DPI support. Default is False.
    """

    width: int = 800
    height: int = 600
    title: str = "Mini Arcade"
    resizable: bool = False
    high_dpi: bool = False


@dataclass(frozen=True)
class RendererSettings:
    """
    Configuration for the renderer (not implemented).

    :ivar background_color (Color): Background color as (r,g,b, optional alpha).
    """

    background_color: Color = (0, 0, 0)

    def rgba(self) -> tuple[int, int, int, int]:
        """
        Get the background color in RGBA format.

        :return: Background color as (r,g,b,a) with alpha as 0-255 integer.
        :rtype: tuple[int, int, int, int]
        """
        return rgba(self.background_color)


@dataclass(frozen=True)
class FontSettings:
    """
    Configuration for font rendering (not implemented).

    :ivar name (str): Name of the font.
    :ivar font_path (Optional[str]): Path to the font file.
    :ivar font_size (int): Default font size.
    """

    name: str = "default"
    path: Optional[str] = None
    size: int = 24


@dataclass(frozen=True)
class AudioSettings:
    """
    Configuration for audio settings (not implemented).

    :ivar enable (bool): Whether to enable audio support.
    :ivar sounds (Optional[dict[str, str]]): Mapping of sound names to file paths.
    """

    enable: bool = False
    sounds: Optional[dict[str, str]] = None


@dataclass(frozen=True)
class BackendSettings:
    """
    Settings for configuring the native backend.

    :ivar window (WindowSettings): Window settings for the backend.
    :ivar renderer (RendererSettings): Renderer settings for the backend.
    :ivar font (FontSettings): Font settings for text rendering.
    :ivar audio (AudioSettings): Audio settings for the backend.
    """

    window: WindowSettings = field(default_factory=WindowSettings)
    renderer: RendererSettings = field(default_factory=RendererSettings)
    fonts: list[FontSettings] = field(default_factory=lambda: [FontSettings()])
    audio: AudioSettings = field(default_factory=AudioSettings)

    def to_dict(self) -> dict:
        """
        Convert the BackendSettings to a dictionary.

        :return: Dictionary representation of the settings.
        :rtype: dict
        """
        return asdict(self)
