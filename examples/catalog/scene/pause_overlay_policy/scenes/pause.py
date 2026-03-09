"""
Pause overlay scene for scene/pause_overlay_policy tutorial example.
"""

from __future__ import annotations

from mini_arcade_core.engine.commands import QuitCommand
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.ui.menu import BaseMenuScene, MenuItem, MenuStyle

from .commands import ResumeOverlayCommand

SCENE_ID = "pause_overlay_policy_pause"


@register_scene(SCENE_ID)
class PauseOverlayPolicyPauseScene(BaseMenuScene):
    """
    Pause overlay scene that receives input while blocking scene below.
    """

    @property
    def menu_title(self) -> str | None:
        return "PAUSED (OVERLAY POLICY)"

    def menu_style(self) -> MenuStyle:
        return MenuStyle(
            overlay_color=(0, 0, 0, 190),
            panel_color=(20, 22, 30, 235),
            button_enabled=True,
            button_fill=(12, 14, 20, 255),
            button_border=(90, 108, 136, 255),
            button_selected_border=(170, 232, 255, 255),
            normal=(225, 230, 238, 255),
            selected=(255, 255, 255, 255),
            hint="ENTER select  ESC resume  F1 debug overlay",
            hint_color=(170, 182, 198, 255),
        )

    def menu_items(self):
        return [
            MenuItem("continue", "CONTINUE", ResumeOverlayCommand),
            MenuItem("quit", "QUIT", QuitCommand),
        ]

