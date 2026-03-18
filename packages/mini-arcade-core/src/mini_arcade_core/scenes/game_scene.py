"""
Game scene base class with replay capture controls enabled.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Callable, ClassVar, Generic, Iterable, Mapping, TypeVar

from mini_arcade_core.backend.keys import Key
from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.sim_scene import SimScene
from mini_arcade_core.scenes.systems.base_system import BaseSystem
from mini_arcade_core.scenes.systems.builtins import (
    ActionSnapshot,
    ConfiguredActionIntentSystem,
    IntentCommandSystem,
    IntentPauseSystem,
)
from mini_arcade_core.scenes.systems.builtins.capture_hotkeys import (
    CaptureHotkey,
    SceneCaptureConfig,
)

# pylint: disable=invalid-name
TContext = TypeVar("TContext")
TWorld = TypeVar("TWorld")
# pylint: enable=invalid-name


@dataclass(frozen=True)
class GameSceneSystemsConfig(Generic[TContext]):
    """
    Declarative configuration for common gameplay scene systems.
    """

    controls_scene_key: str | None = None
    intent_factory: Callable[[ActionSnapshot, TContext], object] | None = None
    input_system_name: str = "action_intent"
    input_channel: str | None = "player_1"
    input_write_to_ctx_intent: bool = True
    input_fallback_bindings: Mapping[str, Any] | None = None
    input_system_factory: (
        Callable[[RuntimeContext], BaseSystem[TContext] | None] | None
    ) = None
    pause_command_factory: Callable[[TContext], object] | None = None
    pause_intent_attr: str = "pause"
    pause_system_name: str = "pause_intent"
    intent_command_bindings: Mapping[str, Callable[[TContext], object]] = (
        field(default_factory=dict)
    )
    intent_commands_system_name: str = "intent_commands"
    extra_system_factories: tuple[
        Callable[[RuntimeContext], BaseSystem[TContext] | None], ...
    ] = ()
    render_system_factory: (
        Callable[[RuntimeContext], BaseSystem[TContext] | None] | None
    ) = None


class GameScene(SimScene[TContext, TWorld], Generic[TContext, TWorld]):
    """
    Scene base class intended for gameplay scenes.
    Enables replay hotkeys by default in addition to screenshot/video.
    """

    capture_config: ClassVar[SceneCaptureConfig] = replace(
        SimScene.capture_config,
        replay_record_toggle=CaptureHotkey(enabled=True, key=Key.F10),
        replay_play_toggle=CaptureHotkey(enabled=True, key=Key.F11),
    )
    auto_systems_enabled: ClassVar[bool] = True
    systems_config: ClassVar[GameSceneSystemsConfig[TContext] | None] = None

    def __init__(self, ctx):
        super().__init__(ctx)
        self._auto_systems_installed = False

    def build_auto_systems(self) -> Iterable[BaseSystem[TContext]]:
        """
        Return built-in/common systems auto-installed for this game scene.

        Subclasses can override to provide input/render/hotkey systems that
        should be attached automatically with no manual pipeline wiring.
        """
        cfg = self.systems_config
        if cfg is None:
            return ()

        systems: list[BaseSystem[TContext]] = []

        if cfg.input_system_factory is not None:
            input_system = cfg.input_system_factory(self.context)
            if input_system is not None:
                systems.append(input_system)
        elif (
            cfg.controls_scene_key is not None
            and cfg.intent_factory is not None
        ):
            systems.append(
                ConfiguredActionIntentSystem(
                    controls=getattr(self.context.settings, "controls", None),
                    scene_key=cfg.controls_scene_key,
                    intent_factory=cfg.intent_factory,
                    fallback_bindings=cfg.input_fallback_bindings,
                    name=cfg.input_system_name,
                    channel=cfg.input_channel,
                    write_to_ctx_intent=cfg.input_write_to_ctx_intent,
                )
            )

        if cfg.pause_command_factory is not None:
            systems.append(
                IntentPauseSystem(
                    pause_command_factory=cfg.pause_command_factory,
                    name=cfg.pause_system_name,
                    intent_attr=cfg.pause_intent_attr,
                )
            )

        if cfg.intent_command_bindings:
            systems.append(
                IntentCommandSystem(
                    bindings=dict(cfg.intent_command_bindings),
                    name=cfg.intent_commands_system_name,
                )
            )

        for system_factory in cfg.extra_system_factories:
            extra_system = system_factory(self.context)
            if extra_system is not None:
                systems.append(extra_system)

        if cfg.render_system_factory is not None:
            render_system = cfg.render_system_factory(self.context)
            if render_system is not None:
                systems.append(render_system)

        return tuple(systems)

    def _ensure_auto_systems(self) -> None:
        if self._auto_systems_installed or not self.auto_systems_enabled:
            return
        self.systems.extend(self.build_auto_systems())
        self._auto_systems_installed = True

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        self._ensure_auto_systems()
        return super().tick(input_frame, dt)
