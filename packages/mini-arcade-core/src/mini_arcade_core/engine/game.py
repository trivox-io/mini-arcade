"""
Game core module defining the Game class and configuration.
"""

from __future__ import annotations

from mini_arcade_core.backend import Backend
from mini_arcade_core.engine.cheats import CheatManager
from mini_arcade_core.engine.commands import CommandQueue
from mini_arcade_core.engine.game_config import GameConfig
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
from mini_arcade_core.engine.scenes.scene_manager import SceneAdapter
from mini_arcade_core.runtime.audio.audio_adapter import SDLAudioAdapter
from mini_arcade_core.runtime.capture.capture_service import CaptureService
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


class Game:
    """Core game object responsible for managing the main loop and active scene."""

    def __init__(
        self, config: GameConfig, scene_registry: SceneRegistry | None = None
    ):
        """
        :param config: Game configuration options.
        :type config: GameConfig

        :param scene_registry: Optional SceneRegistry for scene management.
        :type scene_registry: SceneRegistry | None

        :raises ValueError: If the provided config does not have a valid Backend.
        """
        self.config = config
        self._running: bool = False

        if self.config.backend is None:
            raise ValueError(
                "GameConfig.backend must be set to a Backend instance"
            )

        self.backend: Backend = self.config.backend
        self.settings = GamePlaySettings()
        self.managers = EngineManagers(
            cheats=CheatManager(),
            command_queue=CommandQueue(),
            scenes=SceneAdapter(
                scene_registry or SceneRegistry(_factories={}), self
            ),
        )
        self.services = RuntimeServices(
            window=WindowAdapter(self.backend),
            audio=SDLAudioAdapter(self.backend),
            files=LocalFilesAdapter(),
            capture=CaptureService(
                self.backend
            ),  # NOTE: Should actually be a manager?
            input=InputAdapter(),
            render=RenderService(self.backend),
            scenes=SceneQueryAdapter(self.managers.scenes),
        )

    @property
    def running(self) -> bool:
        """Check if the game is currently running."""
        return self._running

    def quit(self):
        """Request that the main loop stops."""
        self._running = False

    def run(self):
        """
        Run the main loop starting with the given scene.

        This is intentionally left abstract so you can plug pygame, pyglet,
        or another backend.

        :param initial_scene_id: The scene id to start the game with (must be registered).
        :type initial_scene_id: str
        """
        self.managers.scenes.change(self.config.initial_scene)

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

        self.services.window.set_virtual_resolution(800, 600)
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
