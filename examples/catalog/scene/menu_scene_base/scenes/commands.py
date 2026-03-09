"""
Commands for scene/menu_scene_base tutorial example.
"""

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade_core.engine.commands import (
    ChangeSceneCommand,
    Command,
    CommandContext,
)

MENU_SCENE_ID = "menu_scene_base_menu"
PREVIEW_SCENE_ID = "menu_scene_base_preview"
_LEVELS = ("easy", "normal", "hard", "insane")


@dataclass(frozen=True)
class StartPreviewCommand(Command):
    """Change from menu to preview scene."""

    def execute(self, context: CommandContext):
        ChangeSceneCommand(PREVIEW_SCENE_ID).execute(context)


@dataclass(frozen=True)
class BackToMenuCommand(Command):
    """Change from preview back to menu scene."""

    def execute(self, context: CommandContext):
        ChangeSceneCommand(MENU_SCENE_ID).execute(context)


@dataclass(frozen=True)
class CycleDifficultyCommand(Command):
    """
    Cycle gameplay difficulty in runtime settings.
    """

    def execute(self, context: CommandContext):
        difficulty = getattr(context.settings, "difficulty", None)
        if difficulty is None or not hasattr(difficulty, "level"):
            return

        current = str(difficulty.level).lower()
        idx = _LEVELS.index(current) if current in _LEVELS else 0
        difficulty.level = _LEVELS[(idx + 1) % len(_LEVELS)]
