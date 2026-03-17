"""
Custom scene commands demo.

Defines two custom Command subclasses (ResetCounterCommand,
AddScoreCommand) and pushes them from the scene via IntentCommandSystem.
A log panel shows each command as it executes.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from mini_arcade_core.backend import Backend
from mini_arcade_core.backend.keys import Key
from mini_arcade_core.engine.commands import (
    Command,
    CommandContext,
    CommandQueue,
)
from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.sim_scene import SimScene
from mini_arcade_core.scenes.systems.builtins import IntentCommandSystem
from mini_arcade_core.scenes.systems.system_pipeline import SystemPipeline

SCENE_ID = "custom_commands_demo"

_PANEL = (0, 0, 0, 200)
_LABEL = (140, 180, 255)
_VAL = (255, 255, 255)

# Shared mutable state that commands write to.
_state: dict[str, object] = {"score": 0, "log": []}


@dataclass(frozen=True)
class AddScoreCommand(Command):
    """Add points to the score."""

    points: int = 10

    def execute(self, context: CommandContext):
        _state["score"] = int(_state["score"]) + self.points
        log = _state["log"]
        log.append(f"+{self.points} points  (total {_state['score']})")
        if len(log) > 12:
            del log[: len(log) - 12]


@dataclass(frozen=True)
class ResetCounterCommand(Command):
    """Reset the score to zero."""

    def execute(self, context: CommandContext):
        _state["score"] = 0
        log = _state["log"]
        log.append("RESET score to 0")
        if len(log) > 12:
            del log[: len(log) - 12]


@dataclass
class _Intent:
    add_score: bool = False
    reset: bool = False


@dataclass
class _Ctx:
    dt: float = 0.0
    intent: _Intent = field(default_factory=_Intent)
    commands: CommandQueue = field(default_factory=CommandQueue)


@register_scene(SCENE_ID)
class CustomCommandsDemoScene(SimScene):
    """Press Space to add score, R to reset — all driven by commands."""

    def __init__(self, ctx: RuntimeContext):
        super().__init__(ctx)
        _state["score"] = 0
        _state["log"] = []

        self._pipeline: SystemPipeline[_Ctx] = SystemPipeline()
        self._pipeline.add(
            IntentCommandSystem(
                bindings={
                    "add_score": lambda _c: AddScoreCommand(points=10),
                    "reset": lambda _c: ResetCounterCommand(),
                },
            )
        )

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        ctx = _Ctx(
            dt=dt,
            intent=_Intent(
                add_score=Key.SPACE in input_frame.keys_pressed,
                reset=Key.R in input_frame.keys_pressed,
            ),
            commands=self.context.command_queue or CommandQueue(),
        )
        self._pipeline.step(ctx)

        # Execute any commands produced this frame directly for demo purposes.
        for cmd in ctx.commands.drain():
            cmd.execute(
                CommandContext(
                    services=self.context.services,
                    managers=None,
                )
            )

        score = int(_state["score"])
        log = list(_state["log"])

        def draw(backend: Backend):
            r = backend.render
            t = backend.text

            r.draw_rect(16, 16, 768, 568, color=_PANEL)
            y = 28
            t.draw(24, y, "Custom Scene Commands", color=_LABEL)
            y += 28
            t.draw(24, y, f"Score: {score}", color=_VAL)
            y += 28
            t.draw(24, y, "Space = +10 points   R = reset", color=_VAL)
            y += 32

            t.draw(24, y, "Command log:", color=_LABEL)
            y += 22
            for entry in log:
                t.draw(40, y, entry, color=_VAL)
                y += 20

        return RenderPacket.from_ops([draw])
