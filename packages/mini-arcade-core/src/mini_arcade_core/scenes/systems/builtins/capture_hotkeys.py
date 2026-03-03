"""
Reusable capture/replay hotkey system using action-map bindings.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from mini_arcade_core.engine.commands import (
    ScreenshotCommand,
    StartReplayPlayCommand,
    StartReplayRecordCommand,
    StopReplayPlayCommand,
    StopReplayRecordCommand,
    ToggleVideoRecordCommand,
)
from mini_arcade_core.runtime.services import RuntimeServices
from mini_arcade_core.scenes.systems.base_system import BaseSystem
from mini_arcade_core.scenes.systems.builtins.actions import ActionMap


class CaptureContext(Protocol):
    """
    Structural context for capture hotkey systems.
    """

    input_frame: object
    commands: object


# pylint: disable=too-many-instance-attributes
@dataclass(frozen=True)
class CaptureHotkeysConfig:
    """
    Per-scene capture workflow configuration.
    """

    screenshot_label: str | None = None
    replay_file: str | None = None
    replay_game_id: str = "mini-arcade"
    replay_initial_scene: str = "unknown"
    replay_fps: int = 60

    action_toggle_video: str = "capture_toggle_video"
    action_toggle_replay_record: str = "capture_toggle_replay_record"
    action_toggle_replay_play: str = "capture_toggle_replay_play"
    action_screenshot: str = "capture_screenshot"


@dataclass
class CaptureHotkeysSystem(BaseSystem[CaptureContext]):
    """
    Handles screenshot/replay/video commands in a reusable way.
    """

    services: RuntimeServices
    action_map: ActionMap
    cfg: CaptureHotkeysConfig = CaptureHotkeysConfig()
    name: str = "capture_hotkeys"
    order: int = 13

    def step(self, ctx: CaptureContext) -> None:
        snap = self.action_map.read(ctx.input_frame)
        cap = self.services.capture

        if (
            snap.pressed(self.cfg.action_screenshot)
            and self.cfg.screenshot_label
        ):
            ctx.commands.push(
                ScreenshotCommand(label=self.cfg.screenshot_label)
            )

        if snap.pressed(self.cfg.action_toggle_video):
            ctx.commands.push(ToggleVideoRecordCommand())

        if self.cfg.replay_file is None:
            return

        if snap.pressed(self.cfg.action_toggle_replay_record):
            if cap.replay_recording:
                ctx.commands.push(StopReplayRecordCommand())
            else:
                if cap.replay_playing:
                    ctx.commands.push(StopReplayPlayCommand())
                ctx.commands.push(
                    StartReplayRecordCommand(
                        filename=self.cfg.replay_file,
                        game_id=self.cfg.replay_game_id,
                        initial_scene=self.cfg.replay_initial_scene,
                        fps=self.cfg.replay_fps,
                    )
                )

        if snap.pressed(self.cfg.action_toggle_replay_play):
            if cap.replay_playing:
                ctx.commands.push(StopReplayPlayCommand())
            else:
                if cap.replay_recording:
                    ctx.commands.push(StopReplayRecordCommand())
                ctx.commands.push(
                    StartReplayPlayCommand(path=self.cfg.replay_file)
                )
