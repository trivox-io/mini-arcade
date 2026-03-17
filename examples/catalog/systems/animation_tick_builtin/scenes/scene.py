"""
AnimationTickSystem demo scene.

Creates a row of fake "entities" with Anim2D components and uses
AnimationTickSystem to step them.  Since we don't have real textures,
we visualize animation progress as colored rectangles whose hue cycles
through the frame list, demonstrating the system lifecycle.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from mini_arcade_core.backend import Backend
from mini_arcade_core.engine.animation import Animation
from mini_arcade_core.engine.components import Anim2D
from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.sim_scene import SimScene
from mini_arcade_core.scenes.systems.builtins import AnimationTickSystem

SCENE_ID = "animation_tick_demo"

_PANEL = (0, 0, 0, 200)
_LABEL = (140, 180, 255)
_VAL = (255, 255, 255)

# Fake frame IDs (just ints) used to visualize animation state.
_FRAME_IDS = list(range(6))

# Color per frame index for visualization.
_FRAME_COLORS = [
    (255, 80, 80),
    (255, 200, 60),
    (80, 255, 80),
    (60, 200, 255),
    (180, 100, 255),
    (255, 140, 200),
]


@dataclass
class _FakeEntity:
    anim: Anim2D | None = None
    life: object = None
    label: str = ""


@dataclass
class _World:
    entities: list[_FakeEntity] = field(default_factory=list)


def _build_entity(label: str, fps: float, loop: bool) -> _FakeEntity:
    animation = Animation(frames=list(_FRAME_IDS), fps=fps, loop=loop)
    return _FakeEntity(
        anim=Anim2D(anim=animation),
        label=label,
    )


@register_scene(SCENE_ID)
class AnimationTickDemoScene(SimScene):
    """Demonstrates AnimationTickSystem stepping multiple animations."""

    def __init__(self, ctx: RuntimeContext):
        super().__init__(ctx)
        self._world = _World(
            entities=[
                _build_entity("slow (2 fps, loop)", fps=2.0, loop=True),
                _build_entity("normal (6 fps, loop)", fps=6.0, loop=True),
                _build_entity("fast (12 fps, loop)", fps=12.0, loop=True),
                _build_entity("once (4 fps, no loop)", fps=4.0, loop=False),
            ]
        )
        self._anim_system = AnimationTickSystem(
            get_entities=lambda w: w.entities,
        )

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        # Build a minimal context with .world and .dt
        @dataclass
        class _Ctx:
            world: _World
            dt: float

        ctx = _Ctx(world=self._world, dt=dt)
        self._anim_system.step(ctx)

        entities = list(self._world.entities)

        def draw(backend: Backend):
            r = backend.render
            t = backend.text

            r.draw_rect(16, 16, 768, 568, color=_PANEL)
            y = 28
            t.draw(24, y, "AnimationTickSystem Demo", color=_LABEL)
            y += 28
            t.draw(
                24,
                y,
                "Each row is an entity with Anim2D; colored boxes = current frame.",
                color=_VAL,
            )
            y += 32

            for ent in entities:
                t.draw(24, y, ent.label, color=_LABEL)
                y += 22

                # Draw frame strip
                for i, fid in enumerate(_FRAME_IDS):
                    bx = 40 + i * 64
                    is_current = (
                        ent.anim is not None and ent.anim.texture == fid
                    )
                    col = _FRAME_COLORS[i % len(_FRAME_COLORS)]
                    if not is_current:
                        col = (col[0] // 4, col[1] // 4, col[2] // 4)
                    r.draw_rect(bx, y, 56, 40, color=col)
                    t.draw(bx + 20, y + 12, str(fid), color=_VAL)
                y += 52

        return RenderPacket.from_ops([draw])
