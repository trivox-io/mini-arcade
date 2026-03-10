from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _bootstrap_repo_imports() -> None:
    root = _repo_root()
    candidates = [root]
    candidates.extend(path for path in (root / "packages").glob("*/src"))
    candidates.extend(path for path in (root / "games").glob("*/src"))

    for path in reversed(candidates):
        value = str(path)
        if value not in sys.path:
            sys.path.insert(0, value)


_bootstrap_repo_imports()

from mini_arcade_core.engine.entities import BaseEntity  # noqa: E402
from mini_arcade_core.scenes.sim_scene import BaseWorld  # noqa: E402
from mini_arcade_core.scenes.systems.builtins import (  # noqa: E402
    AnimationTickSystem,
    AxisIntentBinding,
    CullOutOfViewportSystem,
    IntentAxisVelocitySystem,
    KinematicMotionSystem,
    MotionBinding,
    ViewportConstraintBinding,
    ViewportConstraintSystem,
)


@dataclass
class _Ctx:
    dt: float
    world: object
    intent: object | None = None


@dataclass
class _World(BaseWorld):
    viewport: tuple[float, float] = (0.0, 0.0)


@dataclass(frozen=True)
class _Intent:
    move_x: float = 0.0


def test_animation_tick_system_advances_anim2d_entities() -> None:
    entity = BaseEntity.from_dict(
        {
            "id": 1,
            "name": "Blink",
            "transform": {
                "center": {"x": 16.0, "y": 16.0},
                "size": {"width": 8.0, "height": 8.0},
            },
            "shape": {"kind": "rect"},
            "anim": {
                "frames": [10, 11],
                "fps": 10.0,
                "loop": True,
            },
            "life": {"alive": True},
        }
    )
    world = _World(entities=[entity])

    AnimationTickSystem(
        get_entities=lambda w: w.entities,
    ).step(_Ctx(dt=0.11, world=world))

    assert entity.anim is not None
    assert entity.anim.texture == 11


def test_cull_out_of_viewport_system_uses_transform_and_life() -> None:
    inside = BaseEntity.from_dict(
        {
            "id": 1,
            "name": "Inside",
            "transform": {
                "center": {"x": 40.0, "y": 50.0},
                "size": {"width": 10.0, "height": 10.0},
            },
            "shape": {"kind": "rect"},
            "life": {"alive": True},
        }
    )
    outside = BaseEntity.from_dict(
        {
            "id": 2,
            "name": "Outside",
            "transform": {
                "center": {"x": 140.0, "y": 50.0},
                "size": {"width": 10.0, "height": 10.0},
            },
            "shape": {"kind": "rect"},
            "life": {"alive": True},
        }
    )
    dead = BaseEntity.from_dict(
        {
            "id": 3,
            "name": "Dead",
            "transform": {
                "center": {"x": 30.0, "y": 30.0},
                "size": {"width": 10.0, "height": 10.0},
            },
            "shape": {"kind": "rect"},
            "life": {"alive": False},
        }
    )
    world = _World(entities=[inside, outside, dead], viewport=(100.0, 100.0))

    CullOutOfViewportSystem(
        viewport_getter=lambda w: w.viewport,
        list_getter=lambda w: w.entities,
        list_setter=lambda w, items: setattr(w, "entities", items),
    ).step(_Ctx(dt=0.0, world=world))

    assert world.entities == [inside]


def test_builtins_package_reexports_utility_systems() -> None:
    assert AnimationTickSystem.__name__ == "AnimationTickSystem"
    assert CullOutOfViewportSystem.__name__ == "CullOutOfViewportSystem"
    assert IntentAxisVelocitySystem.__name__ == "IntentAxisVelocitySystem"
    assert KinematicMotionSystem.__name__ == "KinematicMotionSystem"
    assert ViewportConstraintSystem.__name__ == "ViewportConstraintSystem"


def test_intent_axis_velocity_system_sets_entity_velocity() -> None:
    entity = BaseEntity.from_dict(
        {
            "id": 1,
            "name": "Mover",
            "transform": {
                "center": {"x": 10.0, "y": 10.0},
                "size": {"width": 8.0, "height": 8.0},
            },
            "shape": {"kind": "rect"},
            "kinematic": {
                "velocity": {"vx": 0.0, "vy": 3.0},
                "max_speed": 20.0,
            },
        }
    )
    world = _World(entities=[entity])

    IntentAxisVelocitySystem(
        bindings=(
            AxisIntentBinding(
                entity_getter=lambda ctx: ctx.world.entities[0],
                value_getter=lambda ctx: float(ctx.intent.move_x),
                axis="x",
                zero_other_axis=True,
            ),
        ),
    ).step(_Ctx(dt=0.0, world=world, intent=_Intent(move_x=-0.5)))

    assert entity.kinematic is not None
    assert entity.kinematic.velocity.x == -10.0
    assert entity.kinematic.velocity.y == 0.0


def test_kinematic_motion_system_steps_drag_spin_and_ttl() -> None:
    entity = BaseEntity.from_dict(
        {
            "id": 2,
            "name": "Drifter",
            "transform": {
                "center": {"x": 5.0, "y": 6.0},
                "size": {"width": 4.0, "height": 4.0},
            },
            "shape": {"kind": "rect"},
            "kinematic": {
                "velocity": {"vx": 10.0, "vy": 0.0},
                "max_speed": 20.0,
            },
            "life": {"ttl": 0.05, "alive": True},
        }
    )
    setattr(entity, "spin_deg", 180.0)
    world = _World(entities=[entity])

    KinematicMotionSystem(
        bindings=(
            MotionBinding(
                entities_getter=lambda ctx: ctx.world.entities,
                drag=0.5,
                spin_attr="spin_deg",
                ttl_step=True,
            ),
        ),
    ).step(_Ctx(dt=0.1, world=world))

    assert entity.transform.center.x == 6.0
    assert entity.kinematic is not None
    assert entity.kinematic.velocity.x == 5.0
    assert entity.rotation_deg == 18.0
    assert entity.life is not None
    assert entity.life.alive is False


def test_viewport_constraint_system_clamps_wraps_and_culls() -> None:
    clamped = BaseEntity.from_dict(
        {
            "id": 3,
            "name": "Clamp",
            "transform": {
                "center": {"x": 120.0, "y": 10.0},
                "size": {"width": 10.0, "height": 10.0},
            },
            "shape": {"kind": "rect"},
        }
    )
    wrapped = BaseEntity.from_dict(
        {
            "id": 4,
            "name": "Wrap",
            "transform": {
                "center": {"x": 101.0, "y": 50.0},
                "size": {"width": 10.0, "height": 10.0},
            },
            "shape": {"kind": "rect"},
        }
    )
    culled = BaseEntity.from_dict(
        {
            "id": 5,
            "name": "Cull",
            "transform": {
                "center": {"x": 20.0, "y": 140.0},
                "size": {"width": 10.0, "height": 10.0},
            },
            "shape": {"kind": "rect"},
            "life": {"alive": True},
        }
    )
    world = _World(entities=[clamped, wrapped, culled], viewport=(100.0, 100.0))

    ViewportConstraintSystem(
        bindings=(
            ViewportConstraintBinding(
                entities_getter=lambda ctx: (clamped,),
                policy="clamp",
                axes=("x",),
            ),
            ViewportConstraintBinding(
                entities_getter=lambda ctx: (wrapped,),
                policy="wrap",
                axes=("x",),
            ),
            ViewportConstraintBinding(
                entities_getter=lambda ctx: (culled,),
                policy="cull",
                on_cull=lambda _ctx, entity: setattr(entity.life, "alive", False),
            ),
        ),
    ).step(_Ctx(dt=0.0, world=world))

    assert clamped.transform.center.x == 90.0
    assert wrapped.transform.center.x == 0.0
    assert culled.life is not None
    assert culled.life.alive is False
