"""
Gameplay settings that can be modified during gameplay.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, cast

from mini_arcade_core.engine.render.effects.base import EffectStack

DifficultyType = Literal["easy", "normal", "hard", "insane"]
_VALID_DIFFICULTIES = ("easy", "normal", "hard", "insane")


def _normalize_difficulty(value: Any) -> DifficultyType:
    normalized = str(value).strip().lower()
    if normalized in _VALID_DIFFICULTIES:
        return cast(DifficultyType, normalized)
    return "normal"


@dataclass
class DifficultySettings:
    """
    Settings related to game difficulty that can be modified during gameplay.

    :ivar level (DifficultyType): Current difficulty level.
    """

    level: DifficultyType = "normal"

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "DifficultySettings":
        if not isinstance(data, dict):
            return cls()
        raw_level = data.get("level", data.get("default", "normal"))
        return cls(level=_normalize_difficulty(raw_level))


@dataclass
class GamePlaySettings:
    """
    Game settings that can be modified during gameplay.

    :ivar difficulty (DifficultySettings): Current game difficulty settings.
    """

    difficulty: DifficultySettings = field(default_factory=DifficultySettings)
    effects_stack: EffectStack | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "GamePlaySettings":
        settings = cls()
        if not isinstance(data, dict):
            return settings

        raw_difficulty = data.get("difficulty")
        if isinstance(raw_difficulty, str):
            settings.difficulty = DifficultySettings(
                level=_normalize_difficulty(raw_difficulty)
            )
            return settings

        if isinstance(raw_difficulty, dict):
            settings.difficulty = DifficultySettings.from_dict(
                raw_difficulty
            )

        return settings
