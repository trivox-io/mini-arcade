""" 
Runtime context module.
Defines the RuntimeContext dataclass for game runtime context.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mini_arcade_core.engine.cheats import CheatManager
    from mini_arcade_core.engine.commands import CommandQueue
    from mini_arcade_core.engine.game import Game, GameConfig
    from mini_arcade_core.engine.gameplay_settings import GamePlaySettings
    from mini_arcade_core.runtime.services import RuntimeServices


# TODO: Remove cheats and command_queue from here later if unused.
@dataclass(frozen=True)
class RuntimeContext:
    """
    Context for the game runtime.

    :ivar services (RuntimeServices): Runtime services.
    :ivar config (GameConfig): Game configuration.
    :ivar settings (GamePlaySettings): Game settings.
    :ivar command_queue (CommandQueue | None): Optional command queue.
    :ivar cheats (CheatManager | None): Optional cheat manager.
    """

    services: RuntimeServices
    config: GameConfig
    settings: GamePlaySettings
    command_queue: CommandQueue | None = None
    cheats: CheatManager | None = None

    @staticmethod
    def from_game(game_entity: Game) -> "RuntimeContext":
        """
        Create a RuntimeContext from a Game entity.

        :param game_entity: Game entity to extract context from.
        :type game_entity: Game

        :return: RuntimeContext instance.
        :rtype: RuntimeContext
        """
        return RuntimeContext(
            services=game_entity.services,
            config=game_entity.config,
            settings=game_entity.settings,
            command_queue=game_entity.managers.command_queue,
            cheats=game_entity.managers.cheats,
        )
