from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _bootstrap_repo_imports() -> None:
    root = _repo_root()
    candidates = [root]
    candidates.extend(path for path in (root / "packages").glob("*/src"))
    candidates.extend(path for path in (root / "games").glob("*/src"))
    candidates.extend(path for path in (root / "originals").glob("*/src"))

    for path in reversed(candidates):
        value = str(path)
        if value not in sys.path:
            sys.path.insert(0, value)


_bootstrap_repo_imports()

from mini_arcade_core.engine.entities import BaseEntity  # noqa: E402
from mini_arcade_core.scenes.sim_scene import (  # noqa: E402
    BaseWorld,
    EntityIdDomain,
)
from mini_arcade_core.scenes.systems import SystemPipeline  # noqa: E402
from mini_arcade_core.scenes.systems.builtins import (  # noqa: E402
    AnimationTickSystem,
    ArenaTile,
    AxisIntentBinding,
    BagRandomizer,
    BlockBoard,
    BoardRowClearBinding,
    BoardRowClearSystem,
    BombField,
    BombFuseBinding,
    BombFuseSystem,
    BombPlacementBinding,
    BombPlacementSystem,
    BombState,
    BounceCollisionBinding,
    BounceCollisionSystem,
    BoundsBounceBinding,
    BoundsBounceSystem,
    BrickField,
    BrickFieldCollisionBinding,
    BrickFieldCollisionSystem,
    BrickState,
    CadenceBinding,
    CadenceState,
    CadenceSystem,
    CardinalDirection,
    ChainReactionBinding,
    ChainReactionSystem,
    CollectibleCollisionBinding,
    CollectibleCollisionSystem,
    CollectibleField,
    CollectibleKind,
    CollectibleState,
    ContactDamageBinding,
    ContactDamageSystem,
    ContestantProfile,
    CullOutOfViewportSystem,
    DestructibleTileBinding,
    DestructibleTileSystem,
    ExplosionField,
    ExplosionLifetimeBinding,
    ExplosionLifetimeSystem,
    FallingBlockPiece,
    FallingBlockPieceSpec,
    GridBounds,
    GridCellSpawnBinding,
    GridCellSpawnSystem,
    GridCoord,
    GridLayout,
    GridNavigationBinding,
    GridNavigationSystem,
    GridNavigatorState,
    HazardCollisionBinding,
    HazardCollisionSystem,
    HealthPool,
    IntentAxisVelocitySystem,
    KinematicMotionSystem,
    KnockoutBracketProgressBinding,
    KnockoutBracketProgressSystem,
    KnockoutBracketSeedBinding,
    KnockoutBracketSeedSystem,
    KnockoutBracketState,
    KnockoutMatchResult,
    ModeTimerBinding,
    ModeTimerState,
    ModeTimerSystem,
    MotionBinding,
    PaddleBouncePolicy,
    PickupCollisionBinding,
    PickupCollisionSystem,
    ProceduralParticleBundle,
    ProceduralParticleEmitterState,
    ProceduralParticleSimulationSystem,
    ProjectileLifecycleBinding,
    ProjectileLifecycleBundle,
    ProjectileHitBinding,
    ProjectileHitSystem,
    ScoreChainBinding,
    ScoreChainState,
    ScoreChainSystem,
    SpawnBinding,
    SpawnSystem,
    TileMap,
    TimedMode,
    TimedState,
    TimedStateBinding,
    TimedStateSystem,
    TunnelWrapBinding,
    TunnelWrapSystem,
    ViewportBounceBinding,
    ViewportBounceSystem,
    ViewportConstraintBinding,
    ViewportConstraintSystem,
    WaveProgressionBinding,
    WaveProgressionSystem,
    activate_timed_state,
    arena_tile_map_from_strings,
    available_directions,
    blast_cells,
    block_cells_from_strings,
    build_knockout_layout,
    build_knockout_rounds,
    choose_direction_away,
    choose_direction_toward,
    choose_random_direction,
    claim_knockout_match_winner,
    claim_score_chain_points,
    clear_timed_state,
    damage_health_pool,
    fire_particle_binding,
    free_grid_cells,
    heal_health_pool,
    is_junction,
    is_walkable_arena_tile,
    magic_particle_binding,
    occupied_grid_cells,
    piece_fits,
    playable_knockout_matches,
    project_piece_down,
    reset_score_chain,
    resolve_rect_bounce,
    spawn_explosion_from_bomb,
    step_in_direction,
    tile_map_from_strings,
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


@dataclass
class _RecorderSystem:
    label: str
    seen: list[str]
    name: str = "recorder"

    def step(self, _ctx: object) -> None:
        self.seen.append(self.label)


@dataclass
class _Bundle:
    systems: tuple[object, ...]

    def iter_systems(self) -> Iterable[object]:
        return self.systems


@dataclass
class _BracketCtx:
    world: object


@dataclass
class _BracketWorld:
    entrants: list[ContestantProfile]
    bracket: KnockoutBracketState = field(default_factory=KnockoutBracketState)
    seed_value: int = 9
    should_seed: bool = True
    pending_result: KnockoutMatchResult | None = None


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
    assert BlockBoard.__name__ == "BlockBoard"
    assert BoardRowClearSystem.__name__ == "BoardRowClearSystem"
    assert CadenceSystem.__name__ == "CadenceSystem"
    assert CullOutOfViewportSystem.__name__ == "CullOutOfViewportSystem"
    assert FallingBlockPieceSpec.__name__ == "FallingBlockPieceSpec"
    assert GridCellSpawnSystem.__name__ == "GridCellSpawnSystem"
    assert IntentAxisVelocitySystem.__name__ == "IntentAxisVelocitySystem"
    assert KinematicMotionSystem.__name__ == "KinematicMotionSystem"
    assert ProceduralParticleBundle.__name__ == "ProceduralParticleBundle"
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
    world = _World(
        entities=[clamped, wrapped, culled], viewport=(100.0, 100.0)
    )

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
                on_cull=lambda _ctx, entity: setattr(
                    entity.life, "alive", False
                ),
            ),
        ),
    ).step(_Ctx(dt=0.0, world=world))

    assert clamped.transform.center.x == 90.0
    assert wrapped.transform.center.x == 0.0
    assert culled.life is not None
    assert culled.life.alive is False


def test_system_pipeline_flattens_bundles_into_ordered_systems() -> None:
    seen: list[str] = []
    ctx = object()

    pipeline = SystemPipeline[object]()
    pipeline.add(
        _Bundle(
            systems=(
                _RecorderSystem(label="first", seen=seen, name="first"),
                _RecorderSystem(label="second", seen=seen, name="second"),
            )
        )
    )

    pipeline.step(ctx)

    assert seen == ["first", "second"]


def test_spawn_system_inserts_entities_and_runs_callback() -> None:
    seen: list[int] = []
    world = _World(entities=[])

    SpawnSystem(
        bindings=(
            SpawnBinding(
                should_spawn=lambda _ctx: True,
                spawn=lambda _ctx: BaseEntity.from_dict(
                    {
                        "id": 10,
                        "name": "Spawned",
                        "transform": {
                            "center": {"x": 0.0, "y": 0.0},
                            "size": {"width": 4.0, "height": 4.0},
                        },
                        "shape": {"kind": "rect"},
                    }
                ),
                on_spawned=lambda _ctx, spawned: seen.extend(
                    int(entity.id) for entity in spawned
                ),
            ),
        )
    ).step(_Ctx(dt=0.0, world=world))

    assert [entity.id for entity in world.entities] == [10]
    assert seen == [10]


def test_wave_progression_system_advances_and_spawns_next_wave() -> None:
    @dataclass
    class _WaveWorld(BaseWorld):
        level: int = 1

    world = _WaveWorld(entities=[])

    WaveProgressionSystem(
        bindings=(
            WaveProgressionBinding(
                is_complete=lambda _ctx: True,
                advance=lambda ctx: setattr(
                    ctx.world, "level", ctx.world.level + 1
                ),
                spawn_next=lambda ctx: (
                    BaseEntity.from_dict(
                        {
                            "id": 20 + ctx.world.level,
                            "name": "Wave Enemy",
                            "transform": {
                                "center": {"x": 0.0, "y": 0.0},
                                "size": {"width": 6.0, "height": 6.0},
                            },
                            "shape": {"kind": "rect"},
                        }
                    ),
                ),
            ),
        )
    ).step(_Ctx(dt=0.0, world=world))

    assert world.level == 2
    assert [entity.id for entity in world.entities] == [22]


def test_cadence_system_emits_fixed_interval_ticks() -> None:
    @dataclass
    class _CadenceWorld(BaseWorld):
        cadence: CadenceState = field(default_factory=CadenceState)
        tick_log: list[int] = field(default_factory=list)

    world = _CadenceWorld(entities=[])
    ctx = _Ctx(dt=0.25, world=world)

    CadenceSystem(
        bindings=(
            CadenceBinding(
                state_getter=lambda case: case.world.cadence,
                interval_seconds=0.1,
                max_steps_per_frame=3,
                on_tick=lambda case: case.world.tick_log.append(
                    case.world.cadence.tick_count
                ),
            ),
        )
    ).step(ctx)

    assert world.cadence.steps_this_frame == 2
    assert world.cadence.tick_count == 2
    assert world.tick_log == [1, 2]


def test_grid_helpers_compute_layout_and_free_cells() -> None:
    bounds = GridBounds(cols=4, rows=3)
    layout = GridLayout(
        bounds=bounds,
        cell_width=16.0,
        cell_height=12.0,
        origin_x=8.0,
        origin_y=10.0,
    )

    values = [
        {"cell": GridCoord(col=1, row=0), "alive": True},
        {"cell": GridCoord(col=2, row=1), "alive": False},
        {"cell": GridCoord(col=3, row=2), "alive": True},
    ]
    occupied = occupied_grid_cells(
        values,
        coord_getter=lambda item: item["cell"],
        include=lambda item: bool(item["alive"]),
    )
    free = free_grid_cells(bounds, occupied)

    assert occupied == {GridCoord(col=1, row=0), GridCoord(col=3, row=2)}
    assert GridCoord(col=0, row=0) in free
    assert GridCoord(col=1, row=0) not in free
    assert layout.cell_origin(GridCoord(col=2, row=1)) == (40.0, 22.0)
    assert layout.cell_center(GridCoord(col=2, row=1)) == (48.0, 28.0)
    assert layout.cell_rect(GridCoord(col=2, row=1)) == (
        40.0,
        22.0,
        16.0,
        12.0,
    )


def test_grid_cell_spawn_system_uses_free_cells_only() -> None:
    @dataclass
    class _GridWorld(BaseWorld):
        target_cell: GridCoord | None = None

    world = _GridWorld(entities=[])
    occupied = {GridCoord(col=0, row=0), GridCoord(col=1, row=0)}

    GridCellSpawnSystem(
        bindings=(
            GridCellSpawnBinding(
                should_spawn=lambda _ctx: True,
                bounds_getter=lambda _ctx: GridBounds(cols=3, rows=1),
                occupied_cells_getter=lambda _ctx: occupied,
                choose_cell=lambda _ctx, cells: cells[-1],
                spawn=lambda _ctx, cell: BaseEntity.from_dict(
                    {
                        "id": 50,
                        "name": "Food",
                        "transform": {
                            "center": {
                                "x": float(cell.col),
                                "y": float(cell.row),
                            },
                            "size": {"width": 1.0, "height": 1.0},
                        },
                        "shape": {"kind": "rect"},
                        "tags": ["food"],
                    }
                ),
                on_spawned=lambda ctx, _spawned, cell: setattr(
                    ctx.world, "target_cell", cell
                ),
            ),
        )
    ).step(_Ctx(dt=0.0, world=world))

    assert len(world.entities) == 1
    assert world.target_cell == GridCoord(col=2, row=0)
    assert world.entities[0].transform.center.x == 2.0


def test_block_board_piece_fit_and_row_clear_system() -> None:
    board = BlockBoard[str](cols=4, rows=4)
    board.set(GridCoord(col=0, row=3), "A")
    board.set(GridCoord(col=1, row=3), "A")
    board.set(GridCoord(col=2, row=3), "A")

    piece_spec = FallingBlockPieceSpec(
        name="I2",
        rotations=(
            (
                GridCoord(col=0, row=0),
                GridCoord(col=1, row=0),
            ),
            (
                GridCoord(col=0, row=0),
                GridCoord(col=0, row=1),
            ),
        ),
    )
    piece = FallingBlockPiece(
        spec_name="I2",
        origin=GridCoord(col=2, row=0),
        rotation=1,
    )

    assert piece.cells(piece_spec) == (
        GridCoord(col=2, row=0),
        GridCoord(col=2, row=1),
    )
    assert piece_fits(board, piece, piece_spec) is True
    assert (
        piece_fits(
            board,
            piece.translated(drow=3),
            piece_spec,
        )
        is False
    )

    board.set(GridCoord(col=3, row=3), "B")

    @dataclass
    class _BoardWorld(BaseWorld):
        board: BlockBoard[str] = field(
            default_factory=lambda: BlockBoard[str](cols=4, rows=4)
        )
        cleared_rows: tuple[int, ...] = ()

    world = _BoardWorld(entities=[], board=board)
    BoardRowClearSystem(
        bindings=(
            BoardRowClearBinding(
                board_getter=lambda ctx: ctx.world.board,
                on_cleared=lambda ctx, rows: setattr(
                    ctx.world, "cleared_rows", rows
                ),
            ),
        )
    ).step(_Ctx(dt=0.0, world=world))

    assert world.cleared_rows == (3,)
    assert world.board.row_values(0) == (None, None, None, None)


def test_block_cells_from_strings_and_bag_randomizer_are_deterministic() -> (
    None
):
    cells = block_cells_from_strings(
        ".##.",
        "..#.",
    )
    assert cells == (
        GridCoord(col=1, row=0),
        GridCoord(col=2, row=0),
        GridCoord(col=2, row=1),
    )

    left = BagRandomizer(items=("I", "J", "L", "O"), seed=7)
    right = BagRandomizer(items=("I", "J", "L", "O"), seed=7)

    left_draws = [left.next() for _ in range(6)]
    right_draws = [right.next() for _ in range(6)]

    assert left_draws == right_draws
    assert set(left_draws[:4]) == {"I", "J", "L", "O"}


def test_project_piece_down_and_dynamic_cadence_interval() -> None:
    board = BlockBoard[str](cols=4, rows=5)
    board.set(GridCoord(col=1, row=4), "X")
    board.set(GridCoord(col=2, row=4), "X")

    piece_spec = FallingBlockPieceSpec(
        name="O",
        rotations=(
            block_cells_from_strings(
                "##",
                "##",
            ),
        ),
    )
    landed = project_piece_down(
        board,
        FallingBlockPiece(
            spec_name="O",
            origin=GridCoord(col=1, row=0),
        ),
        piece_spec,
    )
    assert landed.origin == GridCoord(col=1, row=2)

    @dataclass
    class _CadenceWorld(BaseWorld):
        interval: float = 0.2
        fired: int = 0

    world = _CadenceWorld(entities=[])
    system = CadenceSystem(
        bindings=(
            CadenceBinding(
                state_getter=lambda ctx: getattr(
                    ctx.world, "cadence", CadenceState()
                ),
                interval_seconds=lambda ctx: ctx.world.interval,
                on_tick=lambda ctx: setattr(
                    ctx.world, "fired", int(ctx.world.fired) + 1
                ),
            ),
        )
    )
    world.cadence = CadenceState()

    system.step(_Ctx(dt=0.1, world=world))
    assert world.fired == 0

    system.step(_Ctx(dt=0.1, world=world))
    assert world.fired == 1

    world.interval = 0.05
    system.step(_Ctx(dt=0.1, world=world))
    assert world.fired == 3


def test_viewport_bounce_and_paddle_policy_shape_ball_motion() -> None:
    ball = BaseEntity.from_dict(
        {
            "id": 70,
            "name": "Ball",
            "transform": {
                "center": {"x": -3.0, "y": -4.0},
                "size": {"width": 8.0, "height": 8.0},
            },
            "shape": {"kind": "rect"},
            "kinematic": {
                "velocity": {"vx": -120.0, "vy": -100.0},
                "max_speed": 240.0,
            },
        }
    )
    paddle = BaseEntity.from_dict(
        {
            "id": 71,
            "name": "Paddle",
            "transform": {
                "center": {"x": 100.0, "y": 180.0},
                "size": {"width": 64.0, "height": 12.0},
            },
            "shape": {"kind": "rect"},
            "kinematic": {
                "velocity": {"vx": 30.0, "vy": 0.0},
                "max_speed": 180.0,
            },
        }
    )
    world = _World(entities=[ball, paddle], viewport=(200.0, 220.0))

    ViewportBounceSystem(
        bindings=(
            ViewportBounceBinding(
                entities_getter=lambda ctx: (ctx.world.entities[0],),
                bounce_bottom=False,
            ),
        )
    ).step(_Ctx(dt=0.0, world=world))

    assert ball.transform.center.x == 0.0
    assert ball.transform.center.y == 0.0
    assert ball.kinematic is not None
    assert ball.kinematic.velocity.x == 120.0
    assert ball.kinematic.velocity.y == 100.0

    ball.transform.center.x = 148.0
    ball.transform.center.y = 174.0
    PaddleBouncePolicy().apply(ball, paddle)

    assert ball.kinematic.velocity.y < 0.0
    assert ball.kinematic.velocity.x > 0.0


def test_bounce_collision_and_brick_field_collision_damage_targets() -> None:
    ball = BaseEntity.from_dict(
        {
            "id": 80,
            "name": "Ball",
            "transform": {
                "center": {"x": 18.0, "y": 18.0},
                "size": {"width": 8.0, "height": 8.0},
            },
            "shape": {"kind": "rect"},
            "kinematic": {
                "velocity": {"vx": 100.0, "vy": 40.0},
                "max_speed": 220.0,
            },
        }
    )
    paddle = BaseEntity.from_dict(
        {
            "id": 81,
            "name": "Paddle",
            "transform": {
                "center": {"x": 24.0, "y": 18.0},
                "size": {"width": 32.0, "height": 10.0},
            },
            "shape": {"kind": "rect"},
        }
    )
    layout = GridLayout(
        bounds=GridBounds(cols=3, rows=2),
        cell_width=16.0,
        cell_height=8.0,
        origin_x=8.0,
        origin_y=8.0,
    )
    brick_field = BrickField(
        layout=layout,
        bricks={
            GridCoord(col=1, row=0): BrickState(hit_points=2),
        },
    )

    @dataclass
    class _BrickWorld(BaseWorld):
        viewport: tuple[float, float] = (100.0, 100.0)
        brick_field: BrickField | None = None
        brick_hits: list[GridCoord] = field(default_factory=list)

    world = _BrickWorld(entities=[ball, paddle], brick_field=brick_field)

    hit = resolve_rect_bounce(
        (18.0, 18.0, 8.0, 8.0),
        (24.0, 18.0, 32.0, 10.0),
    )
    assert hit is not None
    assert hit.axis == "x"

    BounceCollisionSystem(
        bindings=(
            BounceCollisionBinding(
                mover_getter=lambda ctx: ctx.world.entities[0],
                targets_getter=lambda ctx: (ctx.world.entities[1],),
            ),
        )
    ).step(_Ctx(dt=0.0, world=world))

    assert ball.kinematic is not None
    assert ball.kinematic.velocity.x == -100.0

    ball.transform.center.x = 24.0
    ball.transform.center.y = 8.0
    ball.kinematic.velocity.x = 20.0
    ball.kinematic.velocity.y = 80.0

    BrickFieldCollisionSystem(
        bindings=(
            BrickFieldCollisionBinding(
                mover_getter=lambda ctx: ctx.world.entities[0],
                field_getter=lambda ctx: ctx.world.brick_field,
                on_hit=lambda ctx, _ball, cell, _remaining, _hit: ctx.world.brick_hits.append(
                    cell
                ),
            ),
        )
    ).step(_Ctx(dt=0.0, world=world))

    assert world.brick_hits == [GridCoord(col=1, row=0)]
    assert world.brick_field is not None
    remaining = world.brick_field.brick_at(GridCoord(col=1, row=0))
    assert remaining is not None
    assert remaining.hit_points == 1


def test_pickup_collision_system_collects_overlapping_entities() -> None:
    paddle = BaseEntity.from_dict(
        {
            "id": 90,
            "name": "Paddle",
            "transform": {
                "center": {"x": 80.0, "y": 160.0},
                "size": {"width": 64.0, "height": 12.0},
            },
            "shape": {"kind": "rect"},
        }
    )
    pickup = BaseEntity.from_dict(
        {
            "id": 91,
            "name": "Pickup",
            "transform": {
                "center": {"x": 96.0, "y": 156.0},
                "size": {"width": 18.0, "height": 18.0},
            },
            "shape": {"kind": "rect"},
        }
    )
    missed = BaseEntity.from_dict(
        {
            "id": 92,
            "name": "Missed Pickup",
            "transform": {
                "center": {"x": 12.0, "y": 20.0},
                "size": {"width": 18.0, "height": 18.0},
            },
            "shape": {"kind": "rect"},
        }
    )

    @dataclass
    class _PickupWorld(BaseWorld):
        collected: list[int] = field(default_factory=list)

    world = _PickupWorld(entities=[paddle, pickup, missed])

    PickupCollisionSystem(
        bindings=(
            PickupCollisionBinding(
                collectors_getter=lambda ctx: (ctx.world.entities[0],),
                pickups_getter=lambda ctx: ctx.world.entities[1:],
                on_collect=lambda ctx, _collector, item: ctx.world.collected.append(
                    int(item.id)
                ),
            ),
        )
    ).step(_Ctx(dt=0.0, world=world))

    assert world.collected == [91]
    assert [int(entity.id) for entity in world.entities] == [90, 92]


def test_maze_tile_map_navigation_wrap_collectibles_and_modes() -> None:
    tile_map = tile_map_from_strings(
        "#####",
        "#...#",
        "#...#",
        "#####",
        legend={
            "#": "wall",
            ".": "lane",
        },
        default="void",
    )

    assert step_in_direction(
        GridCoord(col=2, row=1),
        CardinalDirection.RIGHT,
    ) == GridCoord(col=3, row=1)

    options = available_directions(
        tile_map,
        GridCoord(col=2, row=1),
        can_enter=lambda value: value == "lane",
    )
    assert options == (
        CardinalDirection.DOWN,
        CardinalDirection.LEFT,
        CardinalDirection.RIGHT,
    )
    assert (
        is_junction(
            tile_map,
            GridCoord(col=2, row=1),
            can_enter=lambda value: value == "lane",
        )
        is True
    )

    @dataclass
    class _MazeWorld(BaseWorld):
        navigator: GridNavigatorState = field(
            default_factory=lambda: GridNavigatorState(
                cell=GridCoord(col=1, row=1),
                direction=CardinalDirection.RIGHT,
            )
        )
        collectibles: CollectibleField = field(
            default_factory=CollectibleField
        )
        mode_timer: ModeTimerState = field(default_factory=ModeTimerState)
        collected: list[tuple[GridCoord, CollectibleKind]] = field(
            default_factory=list
        )
        mode_log: list[str] = field(default_factory=list)

    world = _MazeWorld(
        entities=[],
        collectibles=CollectibleField(
            items={
                GridCoord(col=1, row=2): CollectibleState(
                    kind=CollectibleKind.PELLET
                ),
            }
        ),
    )
    ctx = _Ctx(dt=0.11, world=world)

    GridNavigationSystem(
        bindings=(
            GridNavigationBinding(
                state_getter=lambda case: case.world.navigator,
                tile_map_getter=lambda _case: tile_map,
                desired_direction_getter=lambda _case: CardinalDirection.DOWN,
                can_enter=lambda value: value == "lane",
                steps_getter=lambda _case: 1,
            ),
        )
    ).step(ctx)

    assert world.navigator.cell == GridCoord(col=1, row=2)
    assert world.navigator.direction == CardinalDirection.DOWN
    assert world.navigator.moved_this_frame == 1

    CollectibleCollisionSystem(
        bindings=(
            CollectibleCollisionBinding(
                collector_cell_getter=lambda case: case.world.navigator.cell,
                field_getter=lambda case: case.world.collectibles,
                on_collect=lambda case, coord, item: case.world.collected.append(
                    (coord, item.kind)
                ),
            ),
        )
    ).step(ctx)

    assert world.collected == [
        (GridCoord(col=1, row=2), CollectibleKind.PELLET)
    ]
    assert world.collectibles.occupied_cells() == ()

    world.navigator.cell = GridCoord(col=-1, row=2)
    TunnelWrapSystem(
        bindings=(
            TunnelWrapBinding(
                states_getter=lambda case: (case.world.navigator,),
                bounds_getter=lambda _case: GridBounds(cols=5, rows=4),
            ),
        )
    ).step(ctx)

    assert world.navigator.cell == GridCoord(col=4, row=2)

    ModeTimerSystem(
        bindings=(
            ModeTimerBinding(
                state_getter=lambda case: case.world.mode_timer,
                schedule=(
                    TimedMode(name="scatter", duration_seconds=0.1),
                    TimedMode(name="chase", duration_seconds=0.1),
                    TimedMode(name="frightened", duration_seconds=None),
                ),
                on_mode_changed=lambda case, mode: case.world.mode_log.append(
                    mode.name
                ),
            ),
        )
    ).step(ctx)

    assert world.mode_timer.current_mode == "chase"
    assert world.mode_log == ["scatter", "chase"]


def test_tile_map_direct_construction_and_collectible_field_lookup() -> None:
    tile_map = TileMap[str](bounds=GridBounds(cols=2, rows=2), default="empty")
    tile_map.set(GridCoord(col=0, row=0), "wall")
    tile_map.set(GridCoord(col=1, row=0), "lane")

    assert tile_map.get(GridCoord(col=0, row=0)) == "wall"
    assert tile_map.get(GridCoord(col=1, row=1)) == "empty"

    field = CollectibleField(
        items={
            GridCoord(col=1, row=1): CollectibleState(
                kind=CollectibleKind.POWER
            )
        }
    )

    assert field.item_at(GridCoord(col=1, row=1)) is not None
    removed = field.remove(GridCoord(col=1, row=1))
    assert removed is not None
    assert removed.kind == CollectibleKind.POWER


def test_maze_direction_choosers_prefer_toward_away_and_random() -> None:
    tile_map = tile_map_from_strings(
        "#####",
        "#...#",
        "#...#",
        "#...#",
        "#####",
        legend={
            "#": "wall",
            ".": "lane",
        },
        default="void",
    )
    origin = GridCoord(col=2, row=2)

    toward = choose_direction_toward(
        tile_map,
        origin,
        GridCoord(col=3, row=2),
        can_enter=lambda value: value == "lane",
        current_direction=CardinalDirection.RIGHT,
    )
    away = choose_direction_away(
        tile_map,
        origin,
        GridCoord(col=3, row=2),
        can_enter=lambda value: value == "lane",
        current_direction=CardinalDirection.RIGHT,
    )
    random_choice = choose_random_direction(
        tile_map,
        origin,
        can_enter=lambda value: value == "lane",
        current_direction=CardinalDirection.RIGHT,
    )

    assert toward == CardinalDirection.RIGHT
    assert away in {
        CardinalDirection.UP,
        CardinalDirection.DOWN,
        CardinalDirection.LEFT,
    }
    assert random_choice in {
        CardinalDirection.UP,
        CardinalDirection.DOWN,
        CardinalDirection.RIGHT,
    }


def test_timed_state_system_expires_active_state() -> None:
    @dataclass
    class _TimedWorld(BaseWorld):
        timer: TimedState = field(default_factory=TimedState)
        expired_tags: list[str] = field(default_factory=list)

    world = _TimedWorld(entities=[])
    activate_timed_state(
        world.timer,
        duration_seconds=0.15,
        tag="frightened",
        payload={"color": "blue"},
    )

    TimedStateSystem(
        bindings=(
            TimedStateBinding(
                state_getter=lambda ctx: ctx.world.timer,
                on_expired=lambda ctx, state: ctx.world.expired_tags.append(
                    state.tag
                ),
            ),
        )
    ).step(_Ctx(dt=0.2, world=world))

    assert world.expired_tags == ["frightened"]
    assert world.timer.active is False
    assert world.timer.remaining_seconds == 0.0
    assert world.timer.payload is None

    activate_timed_state(world.timer, duration_seconds=0.4, tag="bonus")
    clear_timed_state(world.timer)
    assert world.timer.tag == ""


def test_score_chain_system_claims_and_expires_progression() -> None:
    @dataclass
    class _ChainWorld(BaseWorld):
        chain: ScoreChainState = field(default_factory=ScoreChainState)
        expired: int = 0

    world = _ChainWorld(entities=[])
    points = [
        claim_score_chain_points(
            world.chain,
            steps=(200, 400, 800, 1600),
            window_seconds=0.3,
        ),
        claim_score_chain_points(
            world.chain,
            steps=(200, 400, 800, 1600),
            window_seconds=0.3,
        ),
    ]

    assert points == [200, 400]
    assert world.chain.step_index == 2

    ScoreChainSystem(
        bindings=(
            ScoreChainBinding(
                state_getter=lambda ctx: ctx.world.chain,
                on_expired=lambda ctx, _state: setattr(
                    ctx.world,
                    "expired",
                    ctx.world.expired + 1,
                ),
            ),
        )
    ).step(_Ctx(dt=0.5, world=world))

    assert world.expired == 1
    assert world.chain.step_index == 0
    assert world.chain.active is False

    reset_score_chain(world.chain)
    assert world.chain.remaining_seconds == 0.0


def test_projectile_lifecycle_bundle_culls_and_cleans_dead_entities() -> None:
    @dataclass
    class _ProjectileWorld(BaseWorld):
        entity_id_domains = {
            "projectile": EntityIdDomain(start_id=100, end_id=199)
        }
        projectiles: list[int] = field(default_factory=list)
        viewport: tuple[float, float] = (100.0, 100.0)

    projectile = BaseEntity.from_dict(
        {
            "id": 100,
            "name": "Projectile",
            "transform": {
                "center": {"x": 140.0, "y": 10.0},
                "size": {"width": 4.0, "height": 4.0},
            },
            "shape": {"kind": "rect"},
            "kinematic": {
                "velocity": {"vx": 0.0, "vy": 0.0},
                "max_speed": 40.0,
            },
            "life": {"alive": True},
        }
    )
    world = _ProjectileWorld(entities=[projectile], projectiles=[100])

    pipeline = SystemPipeline[_Ctx]()
    pipeline.add(
        ProjectileLifecycleBundle(
            bindings=(
                ProjectileLifecycleBinding(
                    entities_getter=lambda ctx: ctx.world.entities,
                    tracked_ids_attr="projectiles",
                    tracked_domain_name="projectile",
                ),
            ),
            include_motion=False,
            boundary_order=10,
            cleanup_order=11,
        )
    )
    pipeline.step(_Ctx(dt=0.0, world=world))

    assert world.entities == []
    assert world.projectiles == []


def test_bomberman_tile_map_and_bomb_placement_rules() -> None:
    @dataclass
    class _BombWorld(BaseWorld):
        tile_map: TileMap[ArenaTile]
        bombs: BombField = field(default_factory=BombField)
        placement_cell: GridCoord = GridCoord(col=1, row=1)
        placements: list[GridCoord] = field(default_factory=list)

    tile_map = arena_tile_map_from_strings(
        "#####",
        "#S..#",
        "#.*.#",
        "#####",
    )
    world = _BombWorld(entities=[], tile_map=tile_map)

    assert tile_map.get(GridCoord(col=1, row=1)) == ArenaTile.SPAWN
    assert tile_map.get(GridCoord(col=2, row=2)) == ArenaTile.BREAKABLE
    assert (
        is_walkable_arena_tile(tile_map.get(GridCoord(col=1, row=1))) is True
    )
    assert (
        is_walkable_arena_tile(tile_map.get(GridCoord(col=2, row=2))) is False
    )

    system = BombPlacementSystem(
        bindings=(
            BombPlacementBinding(
                should_place=lambda _ctx: True,
                placement_cell_getter=lambda ctx: ctx.world.placement_cell,
                bombs_getter=lambda ctx: ctx.world.bombs,
                tile_map_getter=lambda ctx: ctx.world.tile_map,
                build_bomb=lambda _ctx, cell: BombState(
                    cell=cell,
                    owner_id=7,
                    blast_range=2,
                ),
                owner_id_getter=lambda _ctx: 7,
                max_active_getter=lambda _ctx: 1,
                on_placed=lambda ctx, bomb: ctx.world.placements.append(
                    bomb.cell
                ),
            ),
        )
    )

    system.step(_Ctx(dt=0.0, world=world))
    world.placement_cell = GridCoord(col=2, row=1)
    system.step(_Ctx(dt=0.0, world=world))

    assert world.bombs.count_for_owner(7) == 1
    assert world.placements == [GridCoord(col=1, row=1)]


def test_bomberman_blast_cells_and_destructible_tiles() -> None:
    tile_map = arena_tile_map_from_strings(
        "#######",
        "#..*..#",
        "#.....#",
        "#..#..#",
        "#######",
    )
    origin = GridCoord(col=3, row=2)

    covered = blast_cells(tile_map, origin, blast_range=3)

    assert covered == (
        GridCoord(col=3, row=2),
        GridCoord(col=3, row=1),
        GridCoord(col=2, row=2),
        GridCoord(col=1, row=2),
        GridCoord(col=4, row=2),
        GridCoord(col=5, row=2),
    )

    @dataclass
    class _BombWorld(BaseWorld):
        tile_map: TileMap[ArenaTile]
        explosions: ExplosionField = field(default_factory=ExplosionField)
        destroyed: list[GridCoord] = field(default_factory=list)

    world = _BombWorld(entities=[], tile_map=tile_map)
    for cell in covered:
        world.explosions.set_or_refresh(cell, ttl_seconds=0.2)

    DestructibleTileSystem(
        bindings=(
            DestructibleTileBinding(
                tile_map_getter=lambda ctx: ctx.world.tile_map,
                explosions_getter=lambda ctx: ctx.world.explosions,
                on_destroyed=lambda ctx, cell: ctx.world.destroyed.append(
                    cell
                ),
            ),
        )
    ).step(_Ctx(dt=0.0, world=world))

    assert world.tile_map.get(GridCoord(col=3, row=1)) == ArenaTile.FLOOR
    assert world.destroyed == [GridCoord(col=3, row=1)]


def test_bomberman_fuse_chain_reaction_hazard_and_expiry() -> None:
    @dataclass
    class _Target:
        cell: GridCoord
        alive: bool = True

    @dataclass
    class _BombWorld(BaseWorld):
        tile_map: TileMap[ArenaTile]
        bombs: BombField = field(default_factory=BombField)
        explosions: ExplosionField = field(default_factory=ExplosionField)
        targets: list[_Target] = field(default_factory=list)
        detonated: list[GridCoord] = field(default_factory=list)
        hits: list[GridCoord] = field(default_factory=list)
        expired: list[tuple[GridCoord, ...]] = field(default_factory=list)

    tile_map = arena_tile_map_from_strings(
        "#####",
        "#...#",
        "#...#",
        "#...#",
        "#####",
    )
    world = _BombWorld(
        entities=[],
        tile_map=tile_map,
        targets=[_Target(cell=GridCoord(col=2, row=2))],
    )
    world.bombs.add(
        BombState(
            cell=GridCoord(col=2, row=2),
            fuse_seconds=0.05,
            blast_range=1,
            owner_id=1,
        )
    )
    world.bombs.add(
        BombState(
            cell=GridCoord(col=3, row=2),
            fuse_seconds=1.0,
            blast_range=1,
            owner_id=2,
        )
    )
    ctx = _Ctx(dt=0.1, world=world)

    def _on_detonated(case: _Ctx, bomb: BombState) -> None:
        case.world.detonated.append(bomb.cell)
        spawn_explosion_from_bomb(
            case.world.explosions,
            case.world.tile_map,
            bomb,
            ttl_seconds=0.15,
        )

    fuse_system = BombFuseSystem(
        bindings=(
            BombFuseBinding(
                bombs_getter=lambda case: case.world.bombs,
                on_detonated=_on_detonated,
            ),
        )
    )

    fuse_system.step(ctx)

    ChainReactionSystem(
        bindings=(
            ChainReactionBinding(
                bombs_getter=lambda case: case.world.bombs,
                explosions_getter=lambda case: case.world.explosions,
            ),
        )
    ).step(ctx)

    assert world.bombs.bomb_at(GridCoord(col=3, row=2)) is not None
    assert world.bombs.bomb_at(GridCoord(col=3, row=2)).fuse_seconds == 0.0

    fuse_system.step(_Ctx(dt=0.01, world=world))

    HazardCollisionSystem(
        bindings=(
            HazardCollisionBinding(
                hazard_cells_getter=lambda case: case.world.explosions.active_cells(),
                targets_getter=lambda case: case.world.targets,
                target_cell_getter=lambda _case, target: target.cell,
                on_hit=lambda case, target, cell: (
                    setattr(target, "alive", False),
                    case.world.hits.append(cell),
                ),
            ),
        )
    ).step(_Ctx(dt=0.0, world=world))

    ExplosionLifetimeSystem(
        bindings=(
            ExplosionLifetimeBinding(
                explosions_getter=lambda case: case.world.explosions,
                on_expired=lambda case, cells: case.world.expired.append(
                    cells
                ),
            ),
        )
    ).step(_Ctx(dt=0.2, world=world))

    assert world.detonated == [
        GridCoord(col=2, row=2),
        GridCoord(col=3, row=2),
    ]
    assert world.targets[0].alive is False
    assert GridCoord(col=2, row=2) in world.hits
    assert world.explosions.active_cells() == ()
    assert len(world.expired) == 1


def test_procedural_particle_bundle_spawns_and_renders_particles() -> None:
    @dataclass
    class _ParticleWorld(BaseWorld):
        viewport: tuple[float, float] = (320.0, 240.0)
        fire: ProceduralParticleEmitterState = field(
            default_factory=ProceduralParticleEmitterState
        )
        magic: ProceduralParticleEmitterState = field(
            default_factory=ProceduralParticleEmitterState
        )
        intensity: float = 1.0
        wind: float = 8.0

    @dataclass
    class _ParticleCtx:
        dt: float
        world: _ParticleWorld
        packet: object | None = None

    class _RenderRecorder:
        def __init__(self) -> None:
            self.circles: list[tuple[int, int, int, tuple[int, ...]]] = []
            self.render = self

        def draw_circle(
            self,
            x: int,
            y: int,
            radius: int,
            color=(255, 255, 255),
        ) -> None:
            self.circles.append((int(x), int(y), int(radius), tuple(color)))

    world = _ParticleWorld(entities=[])
    ctx = _ParticleCtx(dt=0.2, world=world)

    bundle = ProceduralParticleBundle(
        bindings=(
            fire_particle_binding(
                state_getter=lambda case: case.world.fire,
                origin_getter=lambda case: (160.0, 190.0),
                intensity_getter=lambda case: case.world.intensity,
                wind_getter=lambda case: case.world.wind,
                viewport_getter=lambda case: case.world.viewport,
                seed=11,
            ),
            magic_particle_binding(
                state_getter=lambda case: case.world.magic,
                origin_getter=lambda case: (160.0, 172.0),
                intensity_getter=lambda case: case.world.intensity * 0.8,
                wind_getter=lambda case: case.world.wind * 0.3,
                viewport_getter=lambda case: case.world.viewport,
                seed=22,
            ),
        )
    )

    pipeline = SystemPipeline[_ParticleCtx]()
    pipeline.add(bundle)
    pipeline.step(ctx)

    assert len(world.fire.particles) > 0
    assert len(world.magic.particles) > 0
    assert ctx.packet is not None

    recorder = _RenderRecorder()
    for op in ctx.packet.ops:
        op(recorder)

    assert recorder.circles


def test_procedural_particle_intensity_changes_spawned_particle_shape() -> (
    None
):
    @dataclass
    class _ParticleWorld(BaseWorld):
        viewport: tuple[float, float] = (320.0, 240.0)
        low: ProceduralParticleEmitterState = field(
            default_factory=ProceduralParticleEmitterState
        )
        high: ProceduralParticleEmitterState = field(
            default_factory=ProceduralParticleEmitterState
        )
        low_intensity: float = 1.0
        high_intensity: float = 2.2

    @dataclass
    class _ParticleCtx:
        dt: float
        world: _ParticleWorld

    world = _ParticleWorld(entities=[])
    ctx = _ParticleCtx(dt=0.2, world=world)

    system = ProceduralParticleSimulationSystem(
        bindings=(
            fire_particle_binding(
                state_getter=lambda case: case.world.low,
                origin_getter=lambda _case: (160.0, 190.0),
                intensity_getter=lambda case: case.world.low_intensity,
                viewport_getter=lambda case: case.world.viewport,
                seed=11,
            ),
            fire_particle_binding(
                state_getter=lambda case: case.world.high,
                origin_getter=lambda _case: (160.0, 190.0),
                intensity_getter=lambda case: case.world.high_intensity,
                viewport_getter=lambda case: case.world.viewport,
                seed=11,
            ),
        )
    )

    system.step(ctx)

    assert world.low.particles
    assert world.high.particles
    assert (
        world.high.particles[0].start_radius
        > world.low.particles[0].start_radius
    )
    assert abs(world.high.particles[0].vy) > abs(world.low.particles[0].vy)
    assert world.high.particles[0].lifetime > world.low.particles[0].lifetime


def test_health_pool_heal_and_damage_clamp_values() -> None:
    pool = HealthPool(current_hp=20.0, max_hp=30.0)

    assert damage_health_pool(pool, 9.0) == 9.0
    assert pool.current_hp == 11.0
    assert pool.alive is True

    assert heal_health_pool(pool, 50.0) == 19.0
    assert pool.current_hp == 30.0

    assert damage_health_pool(pool, 100.0) == 30.0
    assert pool.current_hp == 0.0
    assert pool.alive is False
    assert heal_health_pool(pool, 5.0) == 0.0


def test_contact_damage_system_applies_damage_with_cooldown() -> None:
    attacker = BaseEntity.from_dict(
        {
            "id": 1,
            "name": "Attacker",
            "transform": {
                "center": {"x": 20.0, "y": 20.0},
                "size": {"width": 16.0, "height": 16.0},
            },
            "shape": {"kind": "rect"},
        }
    )
    target = BaseEntity.from_dict(
        {
            "id": 2,
            "name": "Target",
            "transform": {
                "center": {"x": 22.0, "y": 22.0},
                "size": {"width": 16.0, "height": 16.0},
            },
            "shape": {"kind": "rect"},
        }
    )
    target.combat_health = HealthPool(current_hp=30.0, max_hp=30.0)
    hits: list[float] = []
    world = _World(entities=[attacker, target])
    ctx = _Ctx(dt=0.1, world=world)

    system = ContactDamageSystem(
        bindings=(
            ContactDamageBinding(
                attackers_getter=lambda ctx: (attacker,),
                targets_getter=lambda ctx: (target,),
                health_getter=lambda ctx, entity: entity.combat_health,
                damage_getter=lambda ctx, attacker, target: 7.0,
                cooldown_seconds=0.3,
                on_damage=lambda ctx, attacker, target, damage: hits.append(
                    damage
                ),
            ),
        )
    )

    system.step(ctx)
    system.step(ctx)
    assert target.combat_health.current_hp == 23.0
    assert hits == [7.0]

    system.step(_Ctx(dt=0.31, world=world))
    assert target.combat_health.current_hp == 16.0
    assert hits == [7.0, 7.0]


def test_bounds_bounce_system_uses_offset_arena_rect() -> None:
    entity = BaseEntity.from_dict(
        {
            "id": 21,
            "name": "Arena Ball",
            "transform": {
                "center": {"x": 8.0, "y": 18.0},
                "size": {"width": 12.0, "height": 12.0},
            },
            "shape": {"kind": "rect"},
            "kinematic": {
                "velocity": {"vx": -120.0, "vy": -80.0},
            },
        }
    )
    world = _World(entities=[entity])

    BoundsBounceSystem(
        bindings=(
            BoundsBounceBinding(
                entities_getter=lambda ctx: (entity,),
                bounds_getter=lambda ctx: (10.0, 20.0, 100.0, 80.0),
            ),
        )
    ).step(_Ctx(dt=0.1, world=world))

    assert entity.transform.center.x == 10.0
    assert entity.transform.center.y == 20.0
    assert entity.kinematic.velocity.x == 120.0
    assert entity.kinematic.velocity.y == 80.0


def test_projectile_hit_system_damages_target_and_kills_projectile() -> None:
    projectile = BaseEntity.from_dict(
        {
            "id": 10,
            "name": "Bolt",
            "transform": {
                "center": {"x": 40.0, "y": 40.0},
                "size": {"width": 8.0, "height": 8.0},
            },
            "shape": {"kind": "rect"},
        }
    )
    projectile.alive = True
    target = BaseEntity.from_dict(
        {
            "id": 11,
            "name": "Target",
            "transform": {
                "center": {"x": 40.0, "y": 40.0},
                "size": {"width": 18.0, "height": 18.0},
            },
            "shape": {"kind": "rect"},
        }
    )
    target.combat_health = HealthPool(current_hp=24.0, max_hp=24.0)
    hits: list[float] = []
    world = _World(entities=[projectile, target])

    ProjectileHitSystem(
        bindings=(
            ProjectileHitBinding(
                projectiles_getter=lambda ctx: (projectile,),
                targets_getter=lambda ctx: (target,),
                health_getter=lambda ctx, entity: entity.combat_health,
                damage_getter=lambda ctx, projectile, target: 9.0,
                on_hit=lambda ctx, projectile, target, damage: hits.append(
                    damage
                ),
            ),
        )
    ).step(_Ctx(dt=0.1, world=world))

    assert target.combat_health.current_hp == 15.0
    assert projectile.alive is False
    assert hits == [9.0]


def test_knockout_bracket_seed_system_builds_expected_rounds() -> None:
    world = _BracketWorld(
        entrants=[
            ContestantProfile(id=f"entrant_{idx}", name=f"Entrant {idx}")
            for idx in range(16)
        ]
    )
    ctx = _BracketCtx(world=world)

    KnockoutBracketSeedSystem(
        bindings=(
            KnockoutBracketSeedBinding(
                state_getter=lambda ctx: ctx.world.bracket,
                contestants_getter=lambda ctx: ctx.world.entrants,
                seed_getter=lambda ctx: ctx.world.seed_value,
                should_seed=lambda ctx, _state: ctx.world.should_seed,
                on_seeded=lambda ctx, _state: setattr(
                    ctx.world, "should_seed", False
                ),
            ),
        )
    ).step(ctx)

    assert [len(round_matches) for round_matches in world.bracket.rounds] == [
        8,
        4,
        2,
        1,
    ]
    assert len(world.bracket.contestants) == 16
    assert world.bracket.champion_id is None
    assert world.should_seed is False


def test_knockout_bracket_progress_system_advances_winners() -> None:
    world = _BracketWorld(
        entrants=[
            ContestantProfile(id=f"entrant_{idx}", name=f"Entrant {idx}")
            for idx in range(4)
        ]
    )
    ctx = _BracketCtx(world=world)

    KnockoutBracketSeedSystem(
        bindings=(
            KnockoutBracketSeedBinding(
                state_getter=lambda ctx: ctx.world.bracket,
                contestants_getter=lambda ctx: ctx.world.entrants,
                seed_getter=lambda ctx: ctx.world.seed_value,
                should_seed=lambda ctx, _state: ctx.world.should_seed,
                on_seeded=lambda ctx, _state: setattr(
                    ctx.world, "should_seed", False
                ),
            ),
        )
    ).step(ctx)

    first_match = world.bracket.rounds[0][0]
    winner_id = first_match.entrant_a_id
    assert winner_id is not None
    world.pending_result = KnockoutMatchResult(
        match_id=first_match.id,
        winner_id=winner_id,
    )

    KnockoutBracketProgressSystem(
        bindings=(
            KnockoutBracketProgressBinding(
                state_getter=lambda ctx: ctx.world.bracket,
                result_getter=lambda ctx: ctx.world.pending_result,
                clear_result=lambda ctx: setattr(
                    ctx.world, "pending_result", None
                ),
            ),
        )
    ).step(ctx)

    assert world.pending_result is None
    assert world.bracket.rounds[0][0].winner_id == winner_id
    assert world.bracket.rounds[1][0].entrant_a_id == winner_id
    assert world.bracket.rounds[1][0].winner_id is None
    assert world.bracket.champion_id is None
    assert playable_knockout_matches(world.bracket)


def test_knockout_layout_mirrors_around_center_final() -> None:
    state = KnockoutBracketState(
        contestants={
            f"entrant_{idx}": ContestantProfile(
                id=f"entrant_{idx}",
                name=f"Entrant {idx}",
            )
            for idx in range(16)
        }
    )
    state.contestant_ids = list(state.contestants)
    state.rounds = build_knockout_rounds(state.contestant_ids)

    layout = build_knockout_layout(state)
    layout_by_id = {item.match_id: item for item in layout}
    final = layout_by_id[state.rounds[-1][0].id]
    left_round_of_16 = [
        layout_by_id[match.id] for match in state.rounds[0][:4]
    ]
    right_round_of_16 = [
        layout_by_id[match.id] for match in state.rounds[0][4:]
    ]
    left_semifinal = layout_by_id[state.rounds[2][0].id]
    right_semifinal = layout_by_id[state.rounds[2][1].id]

    assert len(layout) == 15
    assert max(item.center.x for item in left_round_of_16) < final.center.x
    assert min(item.center.x for item in right_round_of_16) > final.center.x
    assert left_semifinal.center.x < final.center.x < right_semifinal.center.x
    assert left_round_of_16[0].center.y < left_round_of_16[-1].center.y
    assert right_round_of_16[0].center.y < right_round_of_16[-1].center.y

    left_quarterfinal = layout_by_id[state.rounds[1][0].id]
    right_quarterfinal = layout_by_id[state.rounds[1][3].id]
    assert left_round_of_16[0].center.x + (
        left_round_of_16[0].size.width * 0.5
    ) < left_quarterfinal.center.x - (left_quarterfinal.size.width * 0.5)
    assert right_quarterfinal.center.x + (
        right_quarterfinal.size.width * 0.5
    ) < right_round_of_16[0].center.x - (right_round_of_16[0].size.width * 0.5)
