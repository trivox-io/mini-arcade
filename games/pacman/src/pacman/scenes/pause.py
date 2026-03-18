from __future__ import annotations

from pacman.scenes.commands import BackToMenuCommand, ContinueCommand

from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.ui.menu import BaseMenuScene, MenuItem


@register_scene("pause")
class PauseScene(BaseMenuScene):
    @property
    def menu_title(self) -> str | None:
        return "PAUSED"

    def menu_items(self):
        return [
            MenuItem("continue", "CONTINUE", ContinueCommand),
            MenuItem("menu", "MAIN MENU", BackToMenuCommand),
        ]

    def quit_command(self):
        return ContinueCommand()
