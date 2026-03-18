from mini_arcade_core.engine.commands import (
    Command,
    CommandContext,
    PushSceneIfMissingCommand,
    RemoveSceneCommand,
)
from mini_arcade_core.engine.scenes.models import ScenePolicy


class StartGameCommand(Command):
    def execute(self, context: CommandContext):
        context.managers.scenes.change("play")


class PauseGameCommand(Command):
    def execute(self, context: CommandContext):
        PushSceneIfMissingCommand(
            "pause",
            as_overlay=True,
            policy=ScenePolicy(
                blocks_update=True,
                blocks_input=True,
                is_opaque=False,
                receives_input=True,
            ),
        ).execute(context)


class ContinueCommand(Command):
    def execute(self, context: CommandContext):
        RemoveSceneCommand("pause").execute(context)


class BackToMenuCommand(Command):
    def execute(self, context: CommandContext):
        context.managers.scenes.change("menu")
