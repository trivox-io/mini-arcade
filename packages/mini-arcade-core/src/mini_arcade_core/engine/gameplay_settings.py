"""
Gameplay settings that can be modified during gameplay.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from mini_arcade_core.engine.render.effects.base import EffectStack

Difficulty = Literal["easy", "normal", "hard", "insane"]


@dataclass
class GamePlaySettings:
    """
    Game settings that can be modified during gameplay.

    :ivar difficulty (Difficulty): Current game difficulty level.
    """

    difficulty: Difficulty = "normal"
    effects_stack: EffectStack | None = None
