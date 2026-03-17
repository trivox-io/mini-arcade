"""
Scene stack commands demo.

Three scenes wired together using built-in scene commands:
  - stack_main:  Press 1 → push overlay, 2 → change to alt, Escape → quit
  - stack_overlay: Press Escape → pop back to main
  - stack_alt:     Press Escape → change back to main

Illustrates PushSceneCommand, PopSceneCommand, ChangeSceneCommand.
"""

from __future__ import annotations

from mini_arcade_core.backend import Backend
from mini_arcade_core.backend.keys import Key
from mini_arcade_core.engine.commands import (
    ChangeSceneCommand,
    PopSceneCommand,
    PushSceneIfMissingCommand,
    QuitCommand,
)
from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.sim_scene import SimScene

_PANEL = (0, 0, 0, 200)
_LABEL = (140, 180, 255)
_VAL = (255, 255, 255)


def _push_cmd(cq, cmd):
    if cq is not None:
        cq.push(cmd)


@register_scene("stack_main")
class StackMainScene(SimScene):
    """Primary scene: push overlay (1), change (2), quit (Esc)."""

    def __init__(self, ctx: RuntimeContext):
        super().__init__(ctx)
        self._elapsed = 0.0

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        self._elapsed += dt
        cq = self.context.command_queue

        if Key.NUM_1 in input_frame.keys_pressed:
            _push_cmd(
                cq,
                PushSceneIfMissingCommand(
                    scene_id="stack_overlay", as_overlay=True
                ),
            )
        if Key.NUM_2 in input_frame.keys_pressed:
            _push_cmd(cq, ChangeSceneCommand(scene_id="stack_alt"))
        if Key.ESCAPE in input_frame.keys_pressed:
            _push_cmd(cq, QuitCommand())

        elapsed = self._elapsed

        def draw(backend: Backend):
            r = backend.render
            t = backend.text
            r.draw_rect(16, 16, 768, 568, color=_PANEL)
            t.draw(24, 28, "Scene Stack Commands — Main", color=_LABEL)
            t.draw(24, 60, f"elapsed: {elapsed:.1f}s", color=_VAL)
            t.draw(24, 100, "1 → Push overlay", color=_VAL)
            t.draw(24, 124, "2 → Change to alt scene", color=_VAL)
            t.draw(24, 148, "Escape → Quit", color=_VAL)

        return RenderPacket.from_ops([draw])


@register_scene("stack_overlay")
class StackOverlayScene(SimScene):
    """Overlay: press Escape to pop back."""

    def __init__(self, ctx: RuntimeContext):
        super().__init__(ctx)

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        cq = self.context.command_queue
        if Key.ESCAPE in input_frame.keys_pressed:
            _push_cmd(cq, PopSceneCommand())

        def draw(backend: Backend):
            r = backend.render
            t = backend.text
            r.draw_rect(180, 180, 440, 240, color=(0, 0, 60, 230))
            t.draw(240, 250, "OVERLAY (pushed)", color=(255, 200, 60))
            t.draw(240, 290, "Escape → Pop back to main", color=_VAL)

        return RenderPacket.from_ops([draw])


@register_scene("stack_alt")
class StackAltScene(SimScene):
    """Alternate scene: press Escape to change back to main."""

    def __init__(self, ctx: RuntimeContext):
        super().__init__(ctx)

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        cq = self.context.command_queue
        if Key.ESCAPE in input_frame.keys_pressed:
            _push_cmd(cq, ChangeSceneCommand(scene_id="stack_main"))

        def draw(backend: Backend):
            r = backend.render
            t = backend.text
            r.draw_rect(16, 16, 768, 568, color=(20, 0, 0, 220))
            t.draw(24, 28, "Alternate Scene (changed)", color=(255, 100, 100))
            t.draw(24, 60, "Escape → Change back to main", color=_VAL)

        return RenderPacket.from_ops([draw])
