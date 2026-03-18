from __future__ import annotations

from pacman.scenes.commands import StartGameCommand

from mini_arcade_core.engine.commands import QuitCommand
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.ui.menu import BaseMenuScene, MenuItem


@register_scene("menu")
class MenuScene(BaseMenuScene):
    @property
    def menu_title(self) -> str | None:
        return "PACMAN"

    def menu_items(self):
        return [
            MenuItem("start", "START", StartGameCommand),
            MenuItem("quit", "QUIT", QuitCommand),
        ]
