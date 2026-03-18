"""
Reusable capture/replay hotkey system using action-map bindings.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING, Protocol

from mini_arcade_core.backend.keys import Key
from mini_arcade_core.scenes.systems.base_system import BaseSystem
from mini_arcade_core.scenes.systems.builtins.actions import (
    ActionMap,
    DigitalActionBinding,
)
from mini_arcade_core.scenes.systems.phases import SystemPhase

if TYPE_CHECKING:
    from mini_arcade_core.runtime.services import RuntimeServices


class CaptureContext(Protocol):
    """
    Structural context for capture hotkey systems.
    """

    input_frame: object
    commands: object


@dataclass(frozen=True)
class CaptureHotkey:
    """
    One hotkey toggle configuration.
    """

    enabled: bool = True
    key: Key | None = None


# pylint: disable=too-many-instance-attributes
@dataclass(frozen=True)
class SceneCaptureConfig:
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

    @classmethod
    def from_scene_capture_config(
        cls, cfg: SceneCaptureConfig
    ) -> "CaptureHotkeysConfig":
        """
        Build an action-driven capture config from the scene key config.
        """
        return cls(
            screenshot_label=cfg.screenshot_label,
            replay_file=cfg.replay_file,
            replay_game_id=cfg.replay_game_id,
            replay_initial_scene=cfg.replay_initial_scene or "unknown",
            replay_fps=cfg.replay_fps,
        )


def action_map_from_scene_capture_config(
    scene_cfg: SceneCaptureConfig,
    *,
    hotkeys_cfg: CaptureHotkeysConfig | None = None,
) -> ActionMap:
    """
    Build default capture action bindings from SceneCaptureConfig key hotkeys.
    """
    cfg = hotkeys_cfg or CaptureHotkeysConfig.from_scene_capture_config(
        scene_cfg
    )
    bindings: dict[str, DigitalActionBinding] = {}

    if scene_cfg.screenshot.enabled and scene_cfg.screenshot.key is not None:
        bindings[cfg.action_screenshot] = DigitalActionBinding(
            keys=(scene_cfg.screenshot.key,)
        )

    if (
        scene_cfg.video_toggle.enabled
        and scene_cfg.video_toggle.key is not None
    ):
        bindings[cfg.action_toggle_video] = DigitalActionBinding(
            keys=(scene_cfg.video_toggle.key,)
        )

    if (
        scene_cfg.replay_record_toggle.enabled
        and scene_cfg.replay_record_toggle.key is not None
    ):
        bindings[cfg.action_toggle_replay_record] = DigitalActionBinding(
            keys=(scene_cfg.replay_record_toggle.key,)
        )

    if (
        scene_cfg.replay_play_toggle.enabled
        and scene_cfg.replay_play_toggle.key is not None
    ):
        bindings[cfg.action_toggle_replay_play] = DigitalActionBinding(
            keys=(scene_cfg.replay_play_toggle.key,)
        )

    return ActionMap(bindings=bindings)


@dataclass
class CaptureHotkeysSystem(BaseSystem[CaptureContext]):
    """
    Handles screenshot/replay/video commands in a reusable way.
    """

    services: RuntimeServices
    action_map: ActionMap
    cfg: CaptureHotkeysConfig = CaptureHotkeysConfig()
    name: str = "capture_hotkeys"
    phase: int = SystemPhase.CONTROL
    order: int = 13

    def step(self, ctx: CaptureContext) -> None:
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
