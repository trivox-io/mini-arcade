"""
Command protocol for executing commands with a given context.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Protocol, TypeVar

from mini_arcade_core.engine.scenes.models import ScenePolicy
from mini_arcade_core.runtime.capture.replay_format import ReplayHeader

if TYPE_CHECKING:
    from mini_arcade_core.runtime.services import RuntimeServices

# Justification: Generic type for context
# pylint: disable=invalid-name
TContext = TypeVar("TContext")
# pylint: enable=invalid-name


@dataclass
class CommandContext:
    """
    Context for command execution.

    :ivar services (RuntimeServices): The runtime services.
    :ivar commands (CommandQueue | None): Optional command queue.
    :ivar settings (object | None): Optional settings object.
    :ivar world (object | None): The world object (can be any type).
    """

    services: RuntimeServices
    managers: object
    settings: Optional[object] = None
    world: Optional[object] = None


class Command(Protocol):
    """
    A command is the only allowed "write path" from input/systems into:
    - scene operations (push/pop/change/quit)
    - capture
    - global game lifecycle
    - later: world mutations (if you pass a world reference)

    For now we keep it simple: commands only need RuntimeServices.
    """

    def execute(
        self,
        context: CommandContext,
    ):
        """
        Execute the command with the given world and runtime services.

        :param services: Runtime services for command execution.
        :type services: RuntimeServices

        :param commands: Optional command queue for command execution.
        :type commands: object | None

        :param settings: Optional settings object for command execution.
        :type settings: object | None

        :param world: The world object (can be any type).
        :type world: object | None
        """


@dataclass
class CommandQueue:
    """
    Queue for storing and executing commands.
    """

    _items: List[Command] = field(default_factory=list)

    def push(self, cmd: Command):
        """
        Push a command onto the queue.

        :param cmd: Command to be added to the queue.
        :type cmd: Command
        """
        self._items.append(cmd)

    def drain(self) -> List[Command]:
        """
        Drain and return all commands from the queue.

        :return: List of commands that were in the queue.
        :rtype: list[Command]
        """
        items = self._items
        self._items = []
        return items


@dataclass(frozen=True)
class QuitCommand(Command):
    """Quit the game."""

    def execute(
        self,
        context: CommandContext,
    ):
        context.managers.scenes.quit()


@dataclass(frozen=True)
class ScreenshotCommand(Command):
    """
    Take a screenshot.

    :ivar label (str | None): Optional label for the screenshot file.
    """

    label: str | None = None

    def execute(
        self,
        context: CommandContext,
    ):
        context.services.capture.screenshot(label=self.label)


@dataclass(frozen=True)
class PushSceneCommand(Command):
    """
    Push a new scene onto the scene stack.

    :ivar scene_id (str): Identifier of the scene to push.
    :ivar as_overlay (bool): Whether to push the scene as an overlay.
    """

    scene_id: str
    as_overlay: bool = False

    def execute(
        self,
        context: CommandContext,
    ):
        context.managers.scenes.push(self.scene_id, as_overlay=self.as_overlay)


@dataclass(frozen=True)
class PopSceneCommand(Command):
    """Pop the current scene from the scene stack."""

    def execute(
        self,
        context: CommandContext,
    ):
        context.managers.scenes.pop()


@dataclass(frozen=True)
class ChangeSceneCommand(Command):
    """
    Change the current scene to the specified scene.

    :ivar scene_id (str): Identifier of the scene to switch to.
    """

    scene_id: str

    def execute(
        self,
        context: CommandContext,
    ):
        context.managers.scenes.change(self.scene_id)


@dataclass(frozen=True)
class PushSceneIfMissingCommand(Command):
    """
    Push a scene only if it is not already in the stack.
    """

    scene_id: str
    as_overlay: bool = False
    policy: ScenePolicy | None = None

    def execute(
        self,
        context: CommandContext,
    ):
        scenes = context.managers.scenes
        if scenes.has_scene(self.scene_id):
            return
        scenes.push(
            self.scene_id,
            as_overlay=self.as_overlay,
            policy=self.policy,
        )


@dataclass(frozen=True)
class RemoveSceneCommand(Command):
    """
    Remove a specific scene instance from the scene stack.
    """

    scene_id: str

    def execute(
        self,
        context: CommandContext,
    ):
        context.managers.scenes.remove_scene(self.scene_id)


@dataclass(frozen=True)
class ToggleDebugOverlayCommand(Command):
    """
    Toggle the debug overlay scene.

    :cvar DEBUG_OVERLAY_ID: str: Identifier for the debug overlay scene.
    """

    DEBUG_OVERLAY_ID = "debug_overlay"

    def execute(self, context: CommandContext):
        scenes = context.managers.scenes
        if scenes.has_scene(self.DEBUG_OVERLAY_ID):
            scenes.remove_scene(self.DEBUG_OVERLAY_ID)
            return

        scenes.push(
            self.DEBUG_OVERLAY_ID,
            as_overlay=True,
            policy=ScenePolicy(
                blocks_update=False,
                blocks_input=False,
                is_opaque=False,
                receives_input=False,
            ),
        )


@dataclass(frozen=True)
class ToggleEffectCommand(Command):
    """
    Toggle a post-processing effect on or off.

    :ivar effect_id (str): Identifier of the effect to toggle.
    """

    effect_id: str

    def execute(self, context: CommandContext):
        # effects live in context.meta OR in a dedicated service/settings.
        # v1 simplest: stash stack into context.settings or context.services.render
        stack = getattr(context.settings, "effects_stack", None)
        if stack is None:
            return
        stack.toggle(self.effect_id)


@dataclass(frozen=True)
class StartReplayRecordCommand(Command):
    """
    Start recording a replay to the specified file.

    :ivar filename (str): The filename to save the replay to.
    :ivar game_id (str): Identifier of the game.
    :ivar initial_scene (str): The initial scene of the replay.
    :ivar seed (int): The random seed used in the replay.
    :ivar fps (int): Frames per second for the replay.
    """

    filename: str
    game_id: str = "mini-arcade"
    initial_scene: str = "unknown"
    seed: int = 0
    fps: int = 60

    def execute(self, context: CommandContext):
        header = ReplayHeader(
            game_id=self.game_id,
            initial_scene=self.initial_scene,
            seed=self.seed,
            fps=self.fps,
        )
        context.services.capture.start_replay_record(
            filename=self.filename,
            header=header,
        )


@dataclass(frozen=True)
class StopReplayRecordCommand(Command):
    """Stop recording the current replay."""

    def execute(self, context: CommandContext):
        context.services.capture.stop_replay_record()


@dataclass(frozen=True)
class StartReplayPlayCommand(Command):
    """
    Start playing back a replay from the specified file.

    :ivar path (str): The path to the replay file.
    :ivar change_scene (bool): Whether to change to the replay's initial scene.
    """

    path: str
    change_scene: bool = True

    def execute(self, context: CommandContext):
        header = context.services.capture.start_replay_play(Path(self.path))
        if self.change_scene:
            # NOTE: **IMPORTANT** align game state with the replay header
            context.managers.scenes.change(header.initial_scene)


@dataclass(frozen=True)
class StopReplayPlayCommand(Command):
    """Stop playing back the current replay."""

    def execute(self, context: CommandContext):
        context.services.capture.stop_replay_play()


@dataclass(frozen=True)
class StartVideoRecordCommand(Command):
    """
    Start recording a video.

    :ivar fps (int): Frames per second for the video.
    :ivar capture_fps (int): Frames per second for capturing frames.
    """

    fps: int = 60
    capture_fps: int = 30

    def execute(self, context: CommandContext):
        context.services.capture.start_video_record(
            fps=self.fps, capture_fps=self.capture_fps
        )


@dataclass(frozen=True)
class StopVideoRecordCommand(Command):
    """Stop recording the current video."""

    def execute(self, context: CommandContext):
        context.services.capture.stop_video_record()


@dataclass(frozen=True)
class ToggleVideoRecordCommand(Command):
    """
    Toggle video recording on or off.

    :ivar fps (int): Frames per second for the video.
    :ivar capture_fps (int): Frames per second for capturing frames.
    """

    fps: int = 60
    capture_fps: int = 30

    def execute(self, context: CommandContext):
        cap = context.services.capture
        if cap.video_recording:
            cap.stop_video_record()
        else:
            cap.start_video_record(fps=self.fps, capture_fps=self.capture_fps)
