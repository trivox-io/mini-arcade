"""
Key-driven capture controls shared by all scenes.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING, Protocol

from mini_arcade_core.backend.keys import Key
from mini_arcade_core.scenes.systems.base_system import BaseSystem
from mini_arcade_core.scenes.systems.phases import SystemPhase

if TYPE_CHECKING:
    from mini_arcade_core.runtime.services import RuntimeServices


@dataclass(frozen=True)
class CaptureHotkey:
    """
    One hotkey toggle configuration.
    """

    enabled: bool = True
    key: Key | None = None


@dataclass(frozen=True)
class SceneCaptureConfig:  # pylint: disable=too-many-instance-attributes
    """
    Scene-level capture controls configuration.
    """

    screenshot: CaptureHotkey = field(
        default_factory=lambda: CaptureHotkey(enabled=True, key=Key.F9)
    )
    video_toggle: CaptureHotkey = field(
        default_factory=lambda: CaptureHotkey(enabled=True, key=Key.F12)
    )
    replay_record_toggle: CaptureHotkey = field(
        default_factory=lambda: CaptureHotkey(enabled=False, key=Key.F10)
    )
    replay_play_toggle: CaptureHotkey = field(
        default_factory=lambda: CaptureHotkey(enabled=False, key=Key.F11)
    )
    screenshot_label: str | None = None
    replay_file: str | None = None
    replay_game_id: str = "mini-arcade"
    replay_initial_scene: str | None = None
    replay_fps: int = 60

    def any_enabled(self) -> bool:
        """
        Return True if at least one capture feature is enabled.
        """
        return any(
            (
                self.screenshot.enabled,
                self.video_toggle.enabled,
                self.replay_record_toggle.enabled,
                self.replay_play_toggle.enabled,
            )
        )

    def with_scene_defaults(self, scene_id: str) -> "SceneCaptureConfig":
        """
        Fill scene-derived defaults while preserving explicit overrides.
        """
        replay_file = self.replay_file
        if replay_file is None and (
            self.replay_record_toggle.enabled
            or self.replay_play_toggle.enabled
        ):
            replay_file = f"{scene_id}_replay.marc"

        return replace(
            self,
            screenshot_label=self.screenshot_label or scene_id,
            replay_file=replay_file,
            replay_initial_scene=self.replay_initial_scene or scene_id,
        )


class CaptureControlsContext(Protocol):
    """
    Structural context consumed by CaptureControlsSystem.
    """

    input_frame: object
    commands: object


@dataclass
class CaptureControlsSystem(BaseSystem[CaptureControlsContext]):
    """
    Key-driven capture controls for screenshot/video/replay actions.
    """

    services: RuntimeServices
    cfg: SceneCaptureConfig = field(default_factory=SceneCaptureConfig)
    name: str = "capture_controls"
    phase: int = SystemPhase.CONTROL
    order: int = 13

    @staticmethod
    def _is_triggered(keys_pressed, hotkey: CaptureHotkey) -> bool:
        return bool(
            hotkey.enabled
            and hotkey.key is not None
            and hotkey.key in keys_pressed
        )

    def step(self, ctx: CaptureControlsContext) -> None:
        # Local import avoids a circular import chain:
        # engine.commands -> scenes.models -> scenes.sim_scene -> this module.
        # pylint: disable=import-outside-toplevel
        from mini_arcade_core.engine.commands import (
            ScreenshotCommand,
            StartReplayPlayCommand,
            StartReplayRecordCommand,
            StopReplayPlayCommand,
            StopReplayRecordCommand,
            ToggleVideoRecordCommand,
        )

        # pylint: enable=import-outside-toplevel

        frame = getattr(ctx, "input_frame", None)
        if frame is None:
            return
        keys_pressed = getattr(frame, "keys_pressed", frozenset())

        if self._is_triggered(keys_pressed, self.cfg.screenshot):
            ctx.commands.push(
                ScreenshotCommand(label=self.cfg.screenshot_label)
            )

        if self._is_triggered(keys_pressed, self.cfg.video_toggle):
            ctx.commands.push(ToggleVideoRecordCommand())

        replay_file = self.cfg.replay_file
        if replay_file is None:
            return

        cap = self.services.capture
        if self._is_triggered(keys_pressed, self.cfg.replay_record_toggle):
            if cap.replay_recording:
                ctx.commands.push(StopReplayRecordCommand())
            else:
                if cap.replay_playing:
                    ctx.commands.push(StopReplayPlayCommand())
                ctx.commands.push(
                    StartReplayRecordCommand(
                        filename=replay_file,
                        game_id=self.cfg.replay_game_id,
                        initial_scene=(
                            self.cfg.replay_initial_scene or "unknown"
                        ),
                        fps=self.cfg.replay_fps,
                    )
                )

        if self._is_triggered(keys_pressed, self.cfg.replay_play_toggle):
            if cap.replay_playing:
                ctx.commands.push(StopReplayPlayCommand())
            else:
                if cap.replay_recording:
                    ctx.commands.push(StopReplayRecordCommand())
                ctx.commands.push(StartReplayPlayCommand(path=replay_file))
                ctx.commands.push(StartReplayPlayCommand(path=replay_file))
