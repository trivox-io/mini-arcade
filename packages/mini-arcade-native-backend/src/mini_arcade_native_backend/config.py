"""
Configuration and utility functions for the mini arcade native backend.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

from mini_arcade_core.backend.config import AudioSettings
from mini_arcade_core.backend.config import (
    BackendSettings as CoreBackendSettings,  # pyright: ignore[reportMissingImports]
)
from mini_arcade_core.backend.config import (
    FontSettings,
    RendererSettings,
    WindowSettings,
)

# Justification: native is a compiled extension module.
# pylint: disable=no-name-in-module
from . import _native as native  # type: ignore

# pylint: enable=no-name-in-module


@dataclass(frozen=True)
class NativeBackendSettings:
    """
    Settings for configuring the native backend.

    :ivar core: Core backend settings.
    :ivar api: The rendering API to use.
    """

    core: CoreBackendSettings = field(default_factory=CoreBackendSettings)
    api: native.RenderAPI = native.RenderAPI.SDL2

    def to_dict(self) -> dict:
        """
        Convert the NativeBackendSettings to a dictionary.

        :return: Dictionary representation of the settings.
        :rtype: dict
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "NativeBackendSettings":
        """
        Create a NativeBackendSettings instance from a dictionary.

        :param data: Dictionary containing the settings.
        :type data: dict
        :return: NativeBackendSettings instance.
        :rtype: NativeBackendSettings
        """
        window = WindowSettings(**data.get("window", {}))
        renderer = RendererSettings(**data.get("renderer", {}))
        audio = AudioSettings(**data.get("audio", {}))
        fonts = [FontSettings(**fs) for fs in data.get("fonts", [])]
        return cls(
            core=CoreBackendSettings(
                window=window,
                renderer=renderer,
                audio=audio,
                fonts=fonts,
            ),
            api=native.RenderAPI(data.get("api", native.RenderAPI.SDL2)),
        )
