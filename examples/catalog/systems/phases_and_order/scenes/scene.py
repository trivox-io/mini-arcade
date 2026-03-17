"""
Phases and order scene.

Registers several trivial systems with different phases and orders,
runs them through a SystemPipeline, and displays the execution log
each frame so you can see exactly how order is resolved.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from mini_arcade_core.backend import Backend
from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.sim_scene import SimScene
from mini_arcade_core.scenes.systems.phases import SystemPhase
from mini_arcade_core.scenes.systems.system_pipeline import SystemPipeline

SCENE_ID = "phases_and_order"

_PANEL = (0, 0, 0, 200)
_LABEL = (140, 180, 255)
_VAL = (255, 255, 255)

_PHASE_COLORS = {
    SystemPhase.INPUT: (120, 200, 255),
    SystemPhase.CONTROL: (255, 200, 80),
    SystemPhase.SIMULATION: (100, 255, 100),
    SystemPhase.PRESENTATION: (220, 140, 255),
    SystemPhase.RENDERING: (255, 120, 120),
}


@dataclass
class _DemoContext:
    log: list[str] = field(default_factory=list)


@dataclass
class _TrackerSystem:
    """Tiny system that appends its label to a shared log."""

    name: str
    phase: int
    order: int

    def step(self, ctx: _DemoContext) -> None:
        phase_name = SystemPhase(self.phase).name
        ctx.log.append(
            f"{phase_name}({self.phase}) order={self.order:>3d}  [{self.name}]"
        )


# Build a pipeline with deliberately shuffled insertion order.
_SYSTEMS = [
    _TrackerSystem("render_hud", SystemPhase.RENDERING, 100),
    _TrackerSystem("read_input", SystemPhase.INPUT, 10),
    _TrackerSystem("apply_physics", SystemPhase.SIMULATION, 30),
    _TrackerSystem("move_player", SystemPhase.CONTROL, 20),
    _TrackerSystem("spawn_wave", SystemPhase.SIMULATION, 25),
    _TrackerSystem("animate_sprites", SystemPhase.PRESENTATION, 40),
    _TrackerSystem("apply_drag", SystemPhase.SIMULATION, 35),
    _TrackerSystem("map_actions", SystemPhase.INPUT, 11),
    _TrackerSystem("fire_bullet", SystemPhase.CONTROL, 21),
    _TrackerSystem("cleanup_dead", SystemPhase.SIMULATION, 80),
]


@register_scene(SCENE_ID)
class PhasesAndOrderScene(SimScene):
    """Shows how phase + order determine system execution sequence."""

    def __init__(self, ctx: RuntimeContext):
        super().__init__(ctx)
        self._pipeline: SystemPipeline[_DemoContext] = SystemPipeline()
        for sys in _SYSTEMS:
            self._pipeline.add(sys)

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        demo_ctx = _DemoContext()
        self._pipeline.step(demo_ctx)
        log = demo_ctx.log

        def draw(backend: Backend):
            r = backend.render
            t = backend.text

            r.draw_rect(16, 16, 768, 568, color=_PANEL)

            y = 28
            t.draw(24, y, "System Pipeline: Phases & Order", color=_LABEL)
            y += 28
            t.draw(
                24,
                y,
                "Systems added in random order; pipeline sorts by (phase, order, name).",
                color=_VAL,
            )
            y += 28

            t.draw(24, y, "Execution order this frame:", color=_LABEL)
            y += 24

            for idx, entry in enumerate(log):
                # Determine phase for coloring
                phase_val = int(entry.split("(")[1].split(")")[0])
                try:
                    color = _PHASE_COLORS.get(SystemPhase(phase_val), _VAL)
                except ValueError:
                    color = _VAL
                t.draw(40, y, f"{idx + 1:>2}. {entry}", color=color)
                y += 20

        return RenderPacket.from_ops([draw])
