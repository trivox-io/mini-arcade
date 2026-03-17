"""
Pause intent builtin demo scene.

A bouncing rectangle simulates gameplay while IntentPauseSystem
watches for Escape to push a pause overlay.  Demonstrates the
minimal wiring needed to use the built-in pause system.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from mini_arcade_core.backend import Backend
from mini_arcade_core.backend.keys import Key
from mini_arcade_core.engine.commands import (
    CommandQueue,
    PopSceneCommand,
    PushSceneIfMissingCommand,
)
from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.sim_scene import SimScene
from mini_arcade_core.scenes.systems.builtins import IntentPauseSystem
from mini_arcade_core.scenes.systems.system_pipeline import SystemPipeline

PLAY_SCENE_ID = "pause_intent_demo"
PAUSE_SCENE_ID = "pause_intent_overlay"

_PANEL = (0, 0, 0, 200)
_LABEL = (140, 180, 255)
_VAL = (255, 255, 255)


# -- Play scene --------------------------------------------------------


@dataclass
class _PlayIntent:
    pause: bool = False


@dataclass
class _PlayCtx:
    dt: float = 0.0
    intent: _PlayIntent = field(default_factory=_PlayIntent)
    commands: CommandQueue = field(default_factory=CommandQueue)


@register_scene(PLAY_SCENE_ID)
class PauseIntentDemoScene(SimScene):
    """Bouncing box + IntentPauseSystem driving pause via Escape."""

    def __init__(self, ctx: RuntimeContext):
        super().__init__(ctx)
        self._elapsed = 0.0
        self._pipeline: SystemPipeline[_PlayCtx] = SystemPipeline()
        self._pipeline.add(
            IntentPauseSystem(
                pause_command_factory=lambda _ctx: PushSceneIfMissingCommand(
                    scene_id=PAUSE_SCENE_ID,
                    as_overlay=True,
                ),
            )
        )

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        self._elapsed += dt

        play_ctx = _PlayCtx(
            dt=dt,
            intent=_PlayIntent(
                pause=Key.ESCAPE in input_frame.keys_pressed,
            ),
            commands=self.context.command_queue or CommandQueue(),
        )
        self._pipeline.step(play_ctx)

        elapsed = self._elapsed

        def draw(backend: Backend):
            r = backend.render
            t = backend.text

            r.draw_rect(16, 16, 768, 568, color=_PANEL)
            t.draw(24, 28, "IntentPauseSystem Demo", color=_LABEL)
            t.draw(24, 56, "Press Escape to pause", color=_VAL)
            t.draw(24, 80, f"elapsed: {elapsed:.1f}s", color=_VAL)

            # Bouncing box
            bx = 400 + int(math.sin(elapsed * 2.0) * 150)
            by = 300 + int(math.cos(elapsed * 1.5) * 100)
            r.draw_rect(bx, by, 40, 40, color=(255, 200, 60))

        return RenderPacket.from_ops([draw])


# -- Pause overlay scene -----------------------------------------------


@register_scene(PAUSE_SCENE_ID)
class PauseIntentOverlayScene(SimScene):
    """Simple overlay that pops itself when Escape or Enter is pressed."""

    def __init__(self, ctx: RuntimeContext):
        super().__init__(ctx)

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        if (
            Key.ESCAPE in input_frame.keys_pressed
            or Key.ENTER in input_frame.keys_pressed
        ):
            cq = self.context.command_queue
            if cq is not None:
                cq.push(PopSceneCommand())

        def draw(backend: Backend):
            r = backend.render
            t = backend.text
            r.draw_rect(200, 200, 400, 200, color=(0, 0, 0, 220))
            t.draw(310, 260, "PAUSED", color=(255, 255, 255))
            t.draw(280, 300, "Press Escape / Enter to resume", color=_VAL)

        return RenderPacket.from_ops([draw])
