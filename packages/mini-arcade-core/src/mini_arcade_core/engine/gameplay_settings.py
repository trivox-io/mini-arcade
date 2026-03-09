"""
Gameplay settings that can be modified during gameplay.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Literal, cast

from mini_arcade_core.backend.keys import Key
from mini_arcade_core.engine.render.effects.base import EffectStack

DifficultyType = Literal["easy", "normal", "hard", "insane"]
_VALID_DIFFICULTIES = ("easy", "normal", "hard", "insane")
_DEFAULT_DEBUG_SECTIONS = (
    "timing",
    "render",
    "viewport",
    "effects",
    "stack",
    "scene",
)


def _normalize_difficulty(value: Any) -> DifficultyType:
    normalized = str(value).strip().lower()
    if normalized in _VALID_DIFFICULTIES:
        return cast(DifficultyType, normalized)
    return "normal"


def _normalize_key(value: Any) -> Key | None:
    if isinstance(value, Key):
        return value
    if value is None or value is False:
        return None

    normalized = str(value).strip().upper()
    if not normalized:
        return None
    try:
        return Key[normalized]
    except KeyError:
        return None


def _normalize_color(
    value: Any, default: tuple[int, ...]
) -> tuple[int, ...]:
    if not isinstance(value, (list, tuple)) or not value:
        return default
    out: list[int] = []
    for component in value:
        try:
            out.append(int(component))
        except (TypeError, ValueError):
            return default
    return tuple(out)


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
class DebugOverlayStyleSettings:
    """
    Visual configuration for the built-in debug overlay.
    """

    x: int = 8
    y: int = 8
    width: int = 360
    padding: int = 8
    line_height: int = 18
    font_size: int = 14
    panel_color: tuple[int, ...] = (0, 0, 0, 166)
    text_color: tuple[int, ...] = (255, 255, 255, 255)

    @classmethod
    def from_dict(
        cls, data: dict[str, Any] | None
    ) -> "DebugOverlayStyleSettings":
        if not isinstance(data, dict):
            return cls()
        defaults = cls()
        return cls(
            x=int(data.get("x", defaults.x)),
            y=int(data.get("y", defaults.y)),
            width=int(data.get("width", defaults.width)),
            padding=int(data.get("padding", defaults.padding)),
            line_height=int(data.get("line_height", defaults.line_height)),
            font_size=int(data.get("font_size", defaults.font_size)),
            panel_color=_normalize_color(
                data.get("panel_color"), defaults.panel_color
            ),
            text_color=_normalize_color(
                data.get("text_color"), defaults.text_color
            ),
        )


@dataclass
class DebugOverlaySettings:
    """
    Gameplay-configurable debug overlay settings.
    """

    enabled: bool = False
    start_visible: bool = False
    scene_id: str = "debug_overlay"
    toggle_key: Key | None = Key.F1
    title: str = "Debug Overlay"
    sections: tuple[str, ...] = _DEFAULT_DEBUG_SECTIONS
    static_lines: list[str] = field(default_factory=list)
    style: DebugOverlayStyleSettings = field(
        default_factory=DebugOverlayStyleSettings
    )

    @classmethod
    def from_dict(cls, data: Any) -> "DebugOverlaySettings":
        defaults = cls()
        if isinstance(data, bool):
            return cls(enabled=bool(data))
        if not isinstance(data, dict):
            return defaults

        raw_sections = data.get("sections", list(defaults.sections))
        if isinstance(raw_sections, (list, tuple)):
            sections = tuple(
                str(item).strip().lower()
                for item in raw_sections
                if str(item).strip()
            )
        else:
            sections = defaults.sections

        raw_static_lines = data.get("static_lines", [])
        static_lines = (
            [str(item) for item in raw_static_lines if str(item).strip()]
            if isinstance(raw_static_lines, list)
            else []
        )

        return cls(
            enabled=bool(data.get("enabled", defaults.enabled)),
            start_visible=bool(
                data.get("start_visible", defaults.start_visible)
            ),
            scene_id=str(data.get("scene_id", defaults.scene_id)).strip()
            or defaults.scene_id,
            toggle_key=_normalize_key(
                data.get("toggle_key", defaults.toggle_key)
            ),
            title=str(data.get("title", defaults.title)),
            sections=sections or defaults.sections,
            static_lines=static_lines,
            style=DebugOverlayStyleSettings.from_dict(data.get("style")),
        )


@dataclass
class GamePlaySettings:
    """
    Game settings that can be modified during gameplay.

    :ivar difficulty (DifficultySettings): Current game difficulty settings.
    """

    difficulty: DifficultySettings = field(default_factory=DifficultySettings)
    controls: dict[str, Any] = field(default_factory=dict)
    effects_stack: EffectStack | None = None
    debug_overlay: DebugOverlaySettings = field(
        default_factory=DebugOverlaySettings
    )

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
        elif isinstance(raw_difficulty, dict):
            settings.difficulty = DifficultySettings.from_dict(
                raw_difficulty
            )

        raw_controls = data.get("controls")
        if isinstance(raw_controls, dict):
            settings.controls = deepcopy(raw_controls)

        settings.debug_overlay = DebugOverlaySettings.from_dict(
            data.get("debug_overlay")
        )

        return settings
