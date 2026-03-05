"""
Game scene base class with replay capture controls enabled.
"""

from __future__ import annotations

from dataclasses import replace
from typing import ClassVar, Generic, TypeVar

from mini_arcade_core.backend.keys import Key
from mini_arcade_core.scenes.sim_scene import SimScene
from mini_arcade_core.scenes.systems.capture_controls import (
    CaptureHotkey,
    SceneCaptureConfig,
)

# pylint: disable=invalid-name
TContext = TypeVar("TContext")
TWorld = TypeVar("TWorld")
# pylint: enable=invalid-name


class GameScene(SimScene[TContext, TWorld], Generic[TContext, TWorld]):
    """
    Scene base class intended for gameplay scenes.
    Enables replay hotkeys by default in addition to screenshot/video.
    """

    capture_config: ClassVar[SceneCaptureConfig] = replace(
        SimScene.capture_config,
        replay_record_toggle=CaptureHotkey(enabled=True, key=Key.F10),
        replay_play_toggle=CaptureHotkey(enabled=True, key=Key.F11),
    )
