"""
Commands for scene/pause_overlay_policy tutorial example.
"""

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade_core.engine.commands import (
    Command,
    CommandContext,
    PushSceneIfMissingCommand,
    RemoveSceneCommand,
)
from mini_arcade_core.engine.scenes.models import ScenePolicy

PAUSE_SCENE_ID = "pause_overlay_policy_pause"


@dataclass(frozen=True)
class PauseOverlayCommand(Command):
    """
    Push a pause overlay that blocks update/input below it.
    """

    def execute(self, context: CommandContext):
        PushSceneIfMissingCommand(
            PAUSE_SCENE_ID,
            as_overlay=True,
            policy=ScenePolicy(
                blocks_update=True,
                blocks_input=True,
                is_opaque=False,
                receives_input=True,
            ),
        ).execute(context)


@dataclass(frozen=True)
class ResumeOverlayCommand(Command):
    """
    Resume gameplay by removing pause overlay scene.
    """

    def execute(self, context: CommandContext):
        RemoveSceneCommand(PAUSE_SCENE_ID).execute(context)
