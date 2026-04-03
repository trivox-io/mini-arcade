"""
Game command domain aligned with the stable target architecture.
"""

from .commands import GameRunnerCommand, ScaffoldGameCommand
from .processors import GameRunnerProcessor, GameScaffoldProcessor

__all__ = [
    "GameRunnerCommand",
    "ScaffoldGameCommand",
    "GameRunnerProcessor",
    "GameScaffoldProcessor",
]
