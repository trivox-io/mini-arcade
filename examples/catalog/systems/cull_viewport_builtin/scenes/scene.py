"""
CullOutOfViewportSystem demo scene.

Spawns entities that drift across the screen.  The cull system
removes any that leave the viewport.  A counter tracks spawned vs
alive entities so the effect is visible.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List

from mini_arcade_core.backend import Backend
from mini_arcade_core.engine.entities import BaseEntity
from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.sim_scene import SimScene
from mini_arcade_core.scenes.systems.builtins import CullOutOfViewportSystem
from mini_arcade_core.spaces.geometry.transform import Transform2D
from mini_arcade_core.spaces.math.vec2 import Vec2
from mini_arcade_core.spaces.physics.kinematics2d import Kinematic2D

SCENE_ID = "cull_viewport_demo"

_PANEL = (0, 0, 0, 200)
_LABEL = (140, 180, 255)
_VAL = (255, 255, 255)
_VP = (800.0, 600.0)


def _random_entity(eid: int) -> BaseEntity:
    """Spawn an entity at a random edge heading inward then past."""
    side = random.randint(0, 3)
    if side == 0:  # left
        x, y = -10.0, random.uniform(0, _VP[1])
        vx, vy = random.uniform(60, 180), random.uniform(-40, 40)
    elif side == 1:  # right
        x, y = _VP[0] + 10.0, random.uniform(0, _VP[1])
        vx, vy = random.uniform(-180, -60), random.uniform(-40, 40)
    elif side == 2:  # top
        x, y = random.uniform(0, _VP[0]), -10.0
        vx, vy = random.uniform(-40, 40), random.uniform(60, 180)
    else:  # bottom
        x, y = random.uniform(0, _VP[0]), _VP[1] + 10.0
        vx, vy = random.uniform(-40, 40), random.uniform(-180, -60)

    return BaseEntity.from_dict(
        {
            "id": eid,
            "transform": {
                "center": {"x": x, "y": y},
                "size": {"width": 12, "height": 12},
            },
            "kinematic": {"velocity": {"vx": vx, "vy": vy}, "max_speed": 200},
            "shape": {"kind": "rect"},
            "style": {
                "fill": {
                    "color": [
                        random.randint(100, 255),
                        random.randint(100, 255),
                        random.randint(100, 255),
                    ]
                }
            },
        }
    )


@dataclass
class _World:
    entities: list[BaseEntity] = field(default_factory=list)
    viewport: tuple[float, float] = _VP


@dataclass
class _CullCtx:
    """CullOutOfViewportSystem expects the world under ``ctx.world``."""

    world: _World


@register_scene(SCENE_ID)
class CullViewportDemoScene(SimScene):
    """Spawn drifting entities; CullOutOfViewportSystem removes off-screen ones."""

    def __init__(self, ctx: RuntimeContext):
        super().__init__(ctx)
        self._world = _World()
        self._next_id = 1
        self._spawned_total = 0
        self._culled_total = 0
        self._spawn_timer = 0.0

        self._cull_ctx = _CullCtx(world=self._world)
        self._cull_system = CullOutOfViewportSystem(
            viewport_getter=lambda w: w.viewport,
            list_getter=lambda w: w.entities,
            list_setter=lambda w, lst: setattr(w, "entities", lst),
        )

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        # Spawn a few entities periodically
        self._spawn_timer += dt
        if self._spawn_timer >= 0.15:
            self._spawn_timer = 0.0
            ent = _random_entity(self._next_id)
            self._next_id += 1
            self._spawned_total += 1
            self._world.entities.append(ent)

        # Move entities
        for ent in self._world.entities:
            if ent.kinematic is not None:
                ent.kinematic.step(ent.transform, dt)

        # Cull
        before = len(self._world.entities)
        self._cull_system.step(self._cull_ctx)
        after = len(self._world.entities)
        self._culled_total += before - after

        world_snap = list(self._world.entities)
        spawned = self._spawned_total
        culled = self._culled_total
        alive = len(world_snap)

        def draw(backend: Backend):
            r = backend.render
            t = backend.text

            r.draw_rect(8, 8, 784, 20, color=_PANEL)
            t.draw(
                16,
                10,
                f"spawned: {spawned}  alive: {alive}  culled: {culled}",
                color=_VAL,
            )

            for ent in world_snap:
                x = int(ent.transform.center.x)
                y = int(ent.transform.center.y)
                w = int(ent.transform.size.width)
                h = int(ent.transform.size.height)
                style = ent.style
                fill = getattr(style, "fill", None) if style else None
                color = (
                    tuple(getattr(fill, "color", (255, 255, 255)))
                    if fill
                    else (255, 255, 255)
                )
                r.draw_rect(x, y, w, h, color=color)

        return RenderPacket.from_ops([draw])
