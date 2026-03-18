from __future__ import annotations

from pacman.scenes.commands import PauseGameCommand
from pacman.scenes.play.bootstrap import build_play_world
from pacman.scenes.play.models import PlayIntent, PlayTickContext, PlayWorld
from pacman.scenes.play.pipeline import build_play_systems

from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.bootstrap import scene_viewport
from mini_arcade_core.scenes.game_scene import (
    GameScene,
    GameSceneSystemsConfig,
)


def _build_play_intent(actions, _ctx: PlayTickContext) -> PlayIntent:
    return PlayIntent(
        move_up=actions.pressed("move_up"),
        move_down=actions.pressed("move_down"),
        move_left=actions.pressed("move_left"),
        move_right=actions.pressed("move_right"),
        confirm=actions.pressed("confirm"),
        pause=actions.pressed("pause"),
    )


@register_scene("play")
class PlayScene(GameScene[PlayTickContext, PlayWorld]):
    tick_context_type = PlayTickContext
    systems_config = GameSceneSystemsConfig(
        controls_scene_key="play",
        intent_factory=_build_play_intent,
        input_fallback_bindings={
            "move_up": {
                "type": "digital",
                "keys": ["UP", "W"],
            },
            "move_down": {
                "type": "digital",
                "keys": ["DOWN", "S"],
            },
            "move_left": {
                "type": "digital",
                "keys": ["LEFT", "A"],
            },
            "move_right": {
                "type": "digital",
                "keys": ["RIGHT", "D"],
            },
            "confirm": {
                "type": "digital",
                "keys": ["SPACE", "ENTER"],
            },
            "pause": {
                "type": "digital",
                "keys": ["ESCAPE"],
            },
        },
        pause_command_factory=lambda _ctx: PauseGameCommand(),
    )

    def on_enter(self):
        self.world = build_play_world(viewport=scene_viewport(self))
        self.systems.extend(build_play_systems())
