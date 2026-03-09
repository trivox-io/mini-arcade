"""
Main menu scene for scene/menu_scene_base tutorial example.
"""

from __future__ import annotations

from mini_arcade_core.engine.commands import QuitCommand
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.ui.menu import BaseMenuScene, MenuItem, MenuStyle

from .commands import CycleDifficultyCommand, StartPreviewCommand

SCENE_ID = "menu_scene_base_menu"


@register_scene(SCENE_ID)
class MenuSceneBaseMenuScene(BaseMenuScene):
    """
    Minimal menu scene built on BaseMenuScene.
    """

    @property
    def menu_title(self) -> str | None:
        return "SCENE/MENU_SCENE_BASE"

    def menu_style(self) -> MenuStyle:
        return MenuStyle(
            background_color=(8, 10, 16, 255),
            panel_color=(18, 22, 34, 240),
            button_enabled=True,
            button_fill=(10, 12, 20, 255),
            button_border=(84, 102, 150, 255),
            button_selected_border=(170, 232, 255, 255),
            normal=(220, 228, 238, 255),
            selected=(255, 255, 255, 255),
            hint="UP/DOWN move  ENTER select  ESC quit  F1 debug overlay",
            hint_color=(168, 180, 198, 255),
        )

    @staticmethod
    def _difficulty_label(ctx: RuntimeContext) -> str:
        level = str(ctx.settings.difficulty.level).upper()
        return f"DIFFICULTY: {level}"

    def menu_items(self):
        return [
            MenuItem("start", "START PREVIEW", StartPreviewCommand),
            MenuItem(
                "difficulty",
                "DIFFICULTY",
                CycleDifficultyCommand,
                label_fn=self._difficulty_label,
            ),
            MenuItem("quit", "QUIT", QuitCommand),
        ]

