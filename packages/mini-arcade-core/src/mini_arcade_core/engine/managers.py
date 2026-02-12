"""
Game core module defining the Game class and configuration.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from mini_arcade_core.engine.cheats import CheatManager
from mini_arcade_core.engine.commands import CommandQueue
from mini_arcade_core.engine.scenes.scene_manager import SceneAdapter


@dataclass
class EngineManagers:
    """
    Container for various game managers.

    :ivar cheats (CheatManager): Manager for handling cheat codes.
    """

    cheats: CheatManager = field(default_factory=CheatManager)
    command_queue: CommandQueue = field(default_factory=CommandQueue)
    scenes: SceneAdapter | None = None
