"""
Configuration for the mini-arcade-pygame-backend package.
This is mostly used for packaging and distribution.
It is not used at runtime.
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


@dataclass(frozen=True)
class PygameBackendSettings:
    """
    Settings for configuring the pygame backend.

    :ivar core: Core backend settings.
    :ivar api: The rendering API to use.
    """

    core: CoreBackendSettings = field(default_factory=CoreBackendSettings)

    def to_dict(self) -> dict:
        """
        Convert the PygameBackendSettings to a dictionary.

        :return: Dictionary representation of the settings.
        :rtype: dict
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "PygameBackendSettings":
        """
        Create a PygameBackendSettings instance from a dictionary.

        :param data: Dictionary containing the settings.
        :type data: dict
        :return: PygameBackendSettings instance.
        :rtype: PygameBackendSettings
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
            )
        )
