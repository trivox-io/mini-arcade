"""
Cheat sequences demo scene.

Registers key-sequence cheats with CheatManager and shows a live
buffer readout.  Type the sequences to trigger command callbacks.
"""

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade_core.backend import Backend
from mini_arcade_core.engine.cheats import CheatManager
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

SCENE_ID = "cheat_sequences_demo"

_PANEL = (0, 0, 0, 200)
_LABEL = (140, 180, 255)
_VAL = (255, 255, 255)
_ACTIVATED = (100, 255, 100)

# Shared log
_log: list[str] = []


@dataclass(frozen=True)
class _GodModeCommand(Command):
    def execute(self, context: CommandContext):
        _log.append("GOD MODE activated!")
        if len(_log) > 10:
            del _log[: len(_log) - 10]


@dataclass(frozen=True)
class _MaxLivesCommand(Command):
    def execute(self, context: CommandContext):
        _log.append("MAX LIVES activated!")
        if len(_log) > 10:
            del _log[: len(_log) - 10]


@dataclass(frozen=True)
class _SpeedBoostCommand(Command):
    def execute(self, context: CommandContext):
        _log.append("SPEED BOOST activated!")
        if len(_log) > 10:
            del _log[: len(_log) - 10]


@register_scene(SCENE_ID)
class CheatSequencesDemoScene(SimScene):
    """Type key sequences to trigger cheat commands."""

    def __init__(self, ctx: RuntimeContext):
        super().__init__(ctx)
        _log.clear()

        self._cheats = CheatManager(buffer_size=20)
        self._queue = CommandQueue()

        # Register cheat codes — sequences are uppercase key names.
        self._cheats.register(
            "god_mode",
            sequence=("G", "O", "D"),
            command_factory=lambda _c: _GodModeCommand(),
        )
        self._cheats.register(
            "max_lives",
            sequence=("U", "P", "U", "P"),
            command_factory=lambda _c: _MaxLivesCommand(),
        )
        self._cheats.register(
            "speed_boost",
            sequence=("F", "A", "S", "T"),
            command_factory=lambda _c: _SpeedBoostCommand(),
        )

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        self._cheats.process_frame(
            input_frame,
            context=None,
            queue=self._queue,
        )

        # Execute matched commands
        for cmd in self._queue.drain():
            cmd.execute(
                CommandContext(
                    services=self.context.services,
                    managers=None,
                )
            )

        buffer_str = " ".join(self._cheats._buffer)  # noqa: SLF001
        log_snap = list(_log)

        def draw(backend: Backend):
            r = backend.render
            t = backend.text

            r.draw_rect(16, 16, 768, 568, color=_PANEL)
            y = 28
            t.draw(24, y, "Cheat Sequences Demo", color=_LABEL)
            y += 28

            t.draw(24, y, "Registered cheats:", color=_LABEL)
            y += 22
            t.draw(40, y, "G O D        → God Mode", color=_VAL)
            y += 20
            t.draw(40, y, "U P U P      → Max Lives", color=_VAL)
            y += 20
            t.draw(40, y, "F A S T      → Speed Boost", color=_VAL)
            y += 32

            t.draw(24, y, f"Key buffer: [{buffer_str}]", color=_LABEL)
            y += 32

            t.draw(24, y, "Activated:", color=_LABEL)
            y += 22
            if log_snap:
                for entry in log_snap:
                    t.draw(40, y, entry, color=_ACTIVATED)
                    y += 20
            else:
                t.draw(40, y, "(none yet — type a sequence!)", color=_VAL)

        return RenderPacket.from_ops([draw])
