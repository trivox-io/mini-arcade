"""
Engine and scene configuration classes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PostFXConfig:
    """
    Configuration for post-processing effects.

    :ivar enabled (bool): Whether post effects are enabled by default.
    :ivar active (list[str]): List of active effect IDs by default.
    """

    enabled: bool = True
    active: list[str] = field(default_factory=list)


@dataclass
class SceneConfig:
    """
    Scene bootstrap configuration.

    :ivar initial_scene: Identifier of the initial scene to load.
    :ivar discover_packages: Packages used for scene auto-discovery.
    """

    initial_scene: str = "main"
    discover_packages: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "SceneConfig":
        """
        Construct scene config from a dict, typically parsed from a game config file.

        :param data: The input data to parse.
        :type data: dict or None
        :return: A SceneConfig instance populated with the parsed data.
        :rtype: SceneConfig
        """
        if not isinstance(data, dict):
            return cls()

        discover = data.get("discover_packages", [])
        if not isinstance(discover, list):
            discover = []
        initial_scene = str(data.get("initial_scene", "main")).strip()

        return cls(
            initial_scene=initial_scene,
            discover_packages=[
                str(item) for item in discover if isinstance(item, str)
            ],
        )


@dataclass
class EngineConfig:
    """
    Configuration options for the Engine.

    :ivar fps (int): Target frames per second.
    :ivar virtual_resolution (tuple[int, int]): Virtual render resolution.
    :ivar postfx (PostFXConfig): Configuration for post-processing effects.
    """

    fps: int = 60
    virtual_resolution: tuple[int, int] = (800, 600)
    postfx: PostFXConfig = field(default_factory=PostFXConfig)
    enable_profiler: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EngineConfig":
        """
        Create an EngineConfig instance from a dictionary.

        :param data: Dictionary containing configuration values.
        :type data: dict

        :return: An EngineConfig instance populated with the provided data.
        :rtype: EngineConfig
        """
        defaults = cls()

        raw_virtual_resolution = data.get(
            "virtual_resolution", defaults.virtual_resolution
        )
        if (
            isinstance(raw_virtual_resolution, (list, tuple))
            and len(raw_virtual_resolution) == 2
        ):
            virtual_resolution = (
                int(raw_virtual_resolution[0]),
                int(raw_virtual_resolution[1]),
            )
        else:
            virtual_resolution = defaults.virtual_resolution

        raw_postfx = data.get("postfx")
        if isinstance(raw_postfx, PostFXConfig):
            postfx = raw_postfx
        elif isinstance(raw_postfx, dict):
            active = raw_postfx.get("active", defaults.postfx.active)
            if not isinstance(active, list):
                active = list(defaults.postfx.active)
            postfx = PostFXConfig(
                enabled=bool(
                    raw_postfx.get("enabled", defaults.postfx.enabled)
                ),
                active=[str(item) for item in active],
            )
        else:
            postfx = PostFXConfig(
                enabled=defaults.postfx.enabled,
                active=list(defaults.postfx.active),
            )

        return cls(
            fps=int(data.get("fps", defaults.fps)),
            virtual_resolution=virtual_resolution,
            postfx=postfx,
            enable_profiler=bool(
                data.get("enable_profiler", defaults.enable_profiler)
            ),
        )
