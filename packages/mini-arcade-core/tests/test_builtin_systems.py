from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Iterable
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
from mini_arcade_core.scenes.sim_scene import BaseWorld, EntityIdDomain  # noqa: E402
from mini_arcade_core.scenes.systems import SystemPipeline  # noqa: E402
from mini_arcade_core.scenes.systems.builtins import (  # noqa: E402
    AnimationTickSystem,
    AxisIntentBinding,
    BagRandomizer,
    BlockBoard,
    BoardRowClearBinding,
    BoardRowClearSystem,
    CadenceBinding,
    CadenceState,
    CadenceSystem,
    CullOutOfViewportSystem,
    FallingBlockPiece,
    FallingBlockPieceSpec,
    IntentAxisVelocitySystem,
    KinematicMotionSystem,
    MotionBinding,
    ProceduralParticleBundle,
    ProceduralParticleEmitterState,
    ProceduralParticleSimulationSystem,
    ProjectileLifecycleBinding,
    ProjectileLifecycleBundle,
    SpawnBinding,
    SpawnSystem,
    GridBounds,
    GridCellSpawnBinding,
    GridCellSpawnSystem,
    GridCoord,
    GridLayout,
    ViewportConstraintBinding,
    ViewportConstraintSystem,
    WaveProgressionBinding,
    WaveProgressionSystem,
    block_cells_from_strings,
    free_grid_cells,
    fire_particle_binding,
    magic_particle_binding,
    occupied_grid_cells,
    piece_fits,
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
                advance=lambda ctx: setattr(ctx.world, "level", ctx.world.level + 1),
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
    assert layout.cell_rect(GridCoord(col=2, row=1)) == (40.0, 22.0, 16.0, 12.0)


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
                            "center": {"x": float(cell.col), "y": float(cell.row)},
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
    assert piece_fits(
        board,
        piece.translated(drow=3),
        piece_spec,
    ) is False

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


def test_block_cells_from_strings_and_bag_randomizer_are_deterministic() -> None:
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


def test_procedural_particle_intensity_changes_spawned_particle_shape() -> None:
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
    assert world.high.particles[0].start_radius > world.low.particles[0].start_radius
    assert abs(world.high.particles[0].vy) > abs(world.low.particles[0].vy)
    assert world.high.particles[0].lifetime > world.low.particles[0].lifetime
