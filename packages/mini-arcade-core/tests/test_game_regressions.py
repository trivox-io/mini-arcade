from __future__ import annotations

import sys
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

from dataclasses import dataclass

from asteroids.entities import build_ship  # noqa: E402
from asteroids.entities.entity_id import EntityId as AsteroidsEntityId  # noqa: E402
from deja_bounce.entities import DottedLine, EntityId as PongEntityId  # noqa: E402
from mini_arcade_core.engine.commands import CommandQueue  # noqa: E402
from mini_arcade_core.engine.entities import BaseEntity  # noqa: E402
from mini_arcade_core.engine.gameplay_settings import GamePlaySettings  # noqa: E402
from mini_arcade_core.runtime.context import RuntimeContext  # noqa: E402
from mini_arcade_core.runtime.input_frame import InputFrame  # noqa: E402
from mini_arcade_core.scenes.sim_scene import BaseWorld  # noqa: E402
from space_invaders.entities import Alien, EntityId, Ship  # noqa: E402
from space_invaders.scenes.space_invaders.models import (  # noqa: E402
    SpaceInvadersIntent,
    SpaceInvadersTickContext,
    SpaceInvadersWorld,
)
from space_invaders.scenes.space_invaders.scene import (  # noqa: E402
    SpaceInvadersScene,
)
from space_invaders.scenes.space_invaders.systems import (  # noqa: E402
    BulletSpawnSystem,
    RoundStateSystem,
)


def _runtime_context() -> RuntimeContext:
    return RuntimeContext(
        services=None,  # type: ignore[arg-type]
        config=None,  # type: ignore[arg-type]
        settings=GamePlaySettings(),
        command_queue=CommandQueue(),
        cheats=None,
    )


def _space_invaders_ctx(
    world: SpaceInvadersWorld,
    *,
    intent: SpaceInvadersIntent | None = None,
) -> SpaceInvadersTickContext:
    return SpaceInvadersTickContext(
        input_frame=InputFrame(frame_index=0, dt=1 / 60),
        dt=1 / 60,
        world=world,
        commands=CommandQueue(),
        intent=intent,
    )


def test_pong_dotted_line_template_spans_full_viewport_height() -> None:
    line = DottedLine.build_from_template(
        PongEntityId.CENTER_LINE,
        "Center Line",
        {
            "transform": {
                "size": {
                    "width": 4.0,
                    "height": {"relative": 1.0},
                },
                "position": {
                    "x": {"anchor": "center"},
                    "y": {"anchor": "center"},
                },
            },
            "shape": {
                "kind": "line",
            },
        },
        viewport=(800.0, 600.0),
    )

    assert line.shape.a.y == 0.0
    assert line.shape.b.y == 600.0


def test_space_invaders_shelter_template_keeps_sprite_texture() -> None:
    scene = SpaceInvadersScene(_runtime_context())
    scene._tex = lambda _path: 77  # type: ignore[method-assign]

    resolved = scene._resolve_template({"sprite_full_path": "shelter.png"})

    assert resolved["tex_full"] == 77
    assert resolved["sprite"]["texture"] == 77


def test_space_invaders_bullet_spawn_uses_world_template() -> None:
    ship = Ship.build(
        entity_id=EntityId.SHIP,
        name="Ship",
        x=100.0,
        y=540.0,
        texture=0,
        ship_explosion_frames=[],
    )
    world = SpaceInvadersWorld(
        viewport=(800.0, 600.0),
        entities=[ship],
        bullet_texture=9,
        entity_templates={
            "bullet": {
                "transform": {
                    "size": {"width": 4.0, "height": 10.0},
                },
                "kinematic": {
                    "velocity": {"vx": 0.0, "vy": 0.0},
                    "acceleration": {"ax": 0.0, "ay": 0.0},
                    "max_speed": 400.0,
                },
                "life": {"ttl": 5.0, "alive": True},
            }
        },
    )
    ctx = _space_invaders_ctx(
        world,
        intent=SpaceInvadersIntent(
            move_ship_left=0.0,
            move_ship_right=0.0,
            fire_bullet=True,
        ),
    )

    BulletSpawnSystem().step(ctx)

    assert len(world.bullets) == 1
    bullet = world.get_entity_by_id(world.bullets[0])
    assert bullet is not None
    assert bullet.owner == "ship"


def test_space_invaders_round_ends_when_aliens_reach_bottom() -> None:
    ship = Ship.build(
        entity_id=EntityId.SHIP,
        name="Ship",
        x=100.0,
        y=540.0,
        texture=0,
        ship_explosion_frames=[],
    )
    alien = Alien.build(
        entity_id=EntityId.ALIEN_START,
        name="Alien",
        x=120.0,
        y=590.0,
        frames=[1, 2],
    )
    world = SpaceInvadersWorld(
        viewport=(800.0, 600.0),
        entities=[ship, alien],
    )

    RoundStateSystem().step(_space_invaders_ctx(world))

    assert world.game_over is True


def test_asteroids_template_ship_uses_runtime_ship_id() -> None:
    ship = build_ship(
        template={
            "transform": {
                "size": {"width": 24.0, "height": 28.0},
                "position": {
                    "x": {"anchor": "center"},
                    "y": {"anchor": "middle"},
                },
                "rotation_deg": -90.0,
            },
            "shape": {"kind": "triangle"},
            "collider": {"kind": "circle", "radius": 12.0},
            "kinematic": {
                "velocity": {"vx": 0.0, "vy": 0.0},
                "acceleration": {"ax": 0.0, "ay": 0.0},
                "max_speed": 330.0,
            },
        },
        viewport=(960.0, 720.0),
    )

    assert ship.id == int(AsteroidsEntityId.SHIP)
    assert ship.kinematic is not None


def test_base_entity_from_dict_preserves_z_index() -> None:
    entity = BaseEntity.from_dict(
        {
            "id": 99,
            "name": "Layered Card",
            "z_index": 7,
            "transform": {
                "center": {"x": 10.0, "y": 20.0},
                "size": {"width": 30.0, "height": 40.0},
            },
            "shape": {"kind": "rect"},
        }
    )

    assert entity.z_index == 7


def test_base_world_indexes_stay_in_sync_after_mutation() -> None:
    @dataclass
    class _World(BaseWorld):
        pass

    entity_a = BaseEntity.from_dict(
        {
            "id": 10,
            "name": "A",
            "transform": {
                "center": {"x": 0.0, "y": 0.0},
                "size": {"width": 10.0, "height": 10.0},
            },
            "shape": {"kind": "rect"},
        }
    )
    entity_b = BaseEntity.from_dict(
        {
            "id": 150,
            "name": "B",
            "transform": {
                "center": {"x": 0.0, "y": 0.0},
                "size": {"width": 10.0, "height": 10.0},
            },
            "shape": {"kind": "rect"},
        }
    )
    entity_c = BaseEntity.from_dict(
        {
            "id": 175,
            "name": "C",
            "transform": {
                "center": {"x": 0.0, "y": 0.0},
                "size": {"width": 10.0, "height": 10.0},
            },
            "shape": {"kind": "rect"},
        }
    )

    world = _World(entities=[entity_a, entity_b])

    assert world.get_entity_by_id(10) is entity_a
    assert world.get_entities_by_id_range(100, 199) == [entity_b]

    world.entities.append(entity_c)

    assert world.get_entity_by_id(175) is entity_c
    assert world.get_entities_by_id_range(100, 199) == [entity_b, entity_c]

    world.entities = [entity_c]

    assert world.get_entity_by_id(10) is None
    assert world.get_entity_by_id(175) is entity_c
    assert world.get_entities_by_id_range(100, 199) == [entity_c]
