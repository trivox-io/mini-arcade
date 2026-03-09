"""
Engine core module defining the Engine class and configuration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mini_arcade_core.backend import Backend
from mini_arcade_core.engine.cheats import CheatManager
from mini_arcade_core.engine.commands import CommandQueue
from mini_arcade_core.engine.engine_config import EngineConfig
from mini_arcade_core.engine.gameplay_settings import GamePlaySettings
from mini_arcade_core.engine.loop.config import RunnerConfig
from mini_arcade_core.engine.loop.hooks import DefaultGameHooks
from mini_arcade_core.engine.loop.runner import EngineRunner
from mini_arcade_core.engine.managers import EngineManagers
from mini_arcade_core.engine.render.effects.base import (
    EffectParams,
    EffectStack,
)
from mini_arcade_core.engine.render.effects.crt import CRTEffect
from mini_arcade_core.engine.render.effects.registry import EffectRegistry
from mini_arcade_core.engine.render.effects.vignette import VignetteNoiseEffect
from mini_arcade_core.engine.render.pipeline import RenderPipeline
from mini_arcade_core.engine.render.render_service import RenderService
from mini_arcade_core.engine.scenes.models import ScenePolicy
from mini_arcade_core.engine.scenes.scene_manager import SceneAdapter
from mini_arcade_core.runtime.audio.audio_adapter import SDLAudioAdapter
from mini_arcade_core.runtime.capture.capture_service import CaptureService
from mini_arcade_core.runtime.capture.event_handlers import (
    register_default_capture_event_handlers,
)
from mini_arcade_core.runtime.file.file_adapter import LocalFilesAdapter
from mini_arcade_core.runtime.input.input_adapter import InputAdapter
from mini_arcade_core.runtime.scene.scene_query_adapter import (
    SceneQueryAdapter,
)
from mini_arcade_core.runtime.services import RuntimeServices
from mini_arcade_core.runtime.window.window_adapter import WindowAdapter
from mini_arcade_core.scenes.registry import SceneRegistry
from mini_arcade_core.utils import FrameTimer
from mini_arcade_core.utils.profiler import FrameTimerConfig


@dataclass
class EngineDependencies:
    """
    Runtime dependencies required by the Engine.

    :ivar backend: Backend implementation used by the runtime.
    :ivar scene_registry: Scene registry available to the scene adapter.
    :ivar gameplay_settings: Optional gameplay settings payload.
    """

    backend: Backend
    scene_registry: SceneRegistry = field(
        default_factory=lambda: SceneRegistry(_factories={})
    )
    gameplay_settings: GamePlaySettings | dict[str, Any] | None = None


class Engine:
    """Core engine object responsible for the main loop and active scene."""

    def __init__(
        self,
        config: EngineConfig,
        dependencies: EngineDependencies,
    ):
        """
        :param config: Engine configuration options.
        :type config: EngineConfig

        :param dependencies: Runtime dependencies for this engine instance.
        :type dependencies: EngineDependencies

        :raises ValueError: If a valid Backend instance is not provided.
        """
        self.config = config
        self._running: bool = False

        if dependencies.backend is None:
            raise ValueError(
                "A valid Backend instance must be provided."
            )

        self.backend = dependencies.backend
        gameplay_settings = dependencies.gameplay_settings
        if isinstance(gameplay_settings, GamePlaySettings):
            self.settings = gameplay_settings
        elif isinstance(gameplay_settings, dict):
            self.settings = GamePlaySettings.from_dict(gameplay_settings)
        else:
            self.settings = GamePlaySettings()
        self.managers = EngineManagers(
            cheats=CheatManager(),
            command_queue=CommandQueue(),
            scenes=SceneAdapter(
                dependencies.scene_registry, self
            ),
        )
        self.services = RuntimeServices(
            window=WindowAdapter(self.backend),
            audio=SDLAudioAdapter(self.backend),
            files=LocalFilesAdapter(),
            capture=CaptureService(
                self.backend
            ),
            input=InputAdapter(),
            render=RenderService(self.backend),
            scenes=SceneQueryAdapter(self.managers.scenes),
        )
        register_default_capture_event_handlers()

    @property
    def running(self) -> bool:
        """Check if the game is currently running."""
        return self._running

    def quit(self):
        """Request that the main loop stops."""
        self._running = False

    def run(self, initial_scene: str | None = None):
        """
        Run the main loop starting with the given scene.

        This is intentionally left abstract so you can plug pygame, pyglet,
        or another backend.

        :param initial_scene: Optional scene id to start with.
        :type initial_scene: str | None
        """
        start_scene = initial_scene or "main"
        self.managers.scenes.change(start_scene)
        overlay_cfg = getattr(self.settings, "debug_overlay", None)
        if (
            overlay_cfg is not None
            and overlay_cfg.enabled
            and overlay_cfg.start_visible
            and not self.managers.scenes.has_scene(overlay_cfg.scene_id)
        ):
            self.managers.scenes.push(
                overlay_cfg.scene_id,
                as_overlay=True,
                policy=ScenePolicy(
                    blocks_update=False,
                    blocks_input=False,
                    is_opaque=False,
                    receives_input=False,
                ),
            )

        pipeline = RenderPipeline()
        effects_registry = EffectRegistry()
        effects_registry.register(CRTEffect())
        effects_registry.register(VignetteNoiseEffect())

        effects_stack = EffectStack(
            enabled=self.config.postfx.enabled,
            active=list(self.config.postfx.active),
            params={
                "crt": EffectParams(intensity=0.35, wobble_speed=1.0),
                "vignette_noise": EffectParams(
                    intensity=0.25, wobble_speed=1.0
                ),
            },
        )
        self.settings.effects_stack = effects_stack

        for p in pipeline.passes:
            if getattr(p, "name", "") == "PostFXPass":
                p.registry = effects_registry

        self._running = True

        timer = FrameTimer(
            config=FrameTimerConfig(enabled=self.config.enable_profiler)
        )
        hooks = DefaultGameHooks(self, effects_stack)

        vw, vh = self.config.virtual_resolution
        self.services.window.set_virtual_resolution(int(vw), int(vh))
        runner = EngineRunner(
            self,
            pipeline=pipeline,
            effects_stack=effects_stack,
            hooks=hooks,
        )
        runner.run(cfg=RunnerConfig(fps=self.config.fps), timer=timer)

    def resolve_world(self) -> object | None:
        """
        Resolve and return the current gameplay world.

        :return: The current gameplay world, or None if not found.
        :rtype: object | None
        """
        # Prefer gameplay world underneath overlays:
        # scan from top to bottom and pick the first scene that has .world
        for entry in reversed(self.managers.scenes.visible_entries()):
            scene = entry.scene
            world = getattr(scene, "world", None)
            if world is not None:
                return world
        return None
