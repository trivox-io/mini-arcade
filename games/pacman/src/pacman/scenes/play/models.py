from __future__ import annotations

import random
from dataclasses import dataclass, field

from mini_arcade_core.scenes.sim_scene import (
    BaseIntent,
    BaseTickContext,
    BaseWorld,
)
from mini_arcade_core.scenes.systems.builtins import (
    CadenceState,
    CardinalDirection,
    CollectibleField,
    CollectibleKind,
    CollectibleState,
    GridCoord,
    GridLayout,
    GridNavigatorState,
    ModeTimerState,
    ProceduralParticleEmitterState,
    ScoreChainState,
    TileMap,
    TimedState,
    clear_timed_state,
    reset_score_chain,
)


@dataclass
class GhostState:
    name: str
    color: tuple[int, int, int]
    navigator: GridNavigatorState
    spawn_cell: GridCoord
    start_direction: CardinalDirection
    scatter_target: GridCoord
    desired_direction: CardinalDirection | None = None
    eaten: bool = False

    def reset(self) -> None:
        self.navigator.cell = self.spawn_cell
        self.navigator.direction = self.start_direction
        self.navigator.pending_direction = None
        self.navigator.moved_this_frame = 0
        self.desired_direction = None
        self.eaten = False


@dataclass
class PlayWorld(BaseWorld):
    viewport: tuple[float, float]
    layout: GridLayout
    tile_map: TileMap[str]
    player: GridNavigatorState
    player_start: GridCoord
    player_start_direction: CardinalDirection
    ghosts: list[GhostState]
    collectible_blueprint: tuple[tuple[GridCoord, CollectibleKind], ...]
    collectibles: CollectibleField = field(default_factory=CollectibleField)
    player_cadence: CadenceState = field(default_factory=CadenceState)
    ghost_cadence: CadenceState = field(default_factory=CadenceState)
    mode_timer: ModeTimerState = field(default_factory=ModeTimerState)
    frightened: TimedState = field(default_factory=TimedState)
    ghost_chain: ScoreChainState = field(default_factory=ScoreChainState)
    score: int = 0
    best_score: int = 0
    lives: int = 3
    level: int = 1
    game_over: bool = False
    victory: bool = False
    freeze_timer: float = 1.0
    flash_timer: float = 0.0
    flash_color: tuple[int, int, int] = (72, 92, 255)
    effect_origin: tuple[float, float] = (0.0, 0.0)
    effect_timer: float = 0.0
    effect_intensity: float = 0.0
    status_text: str = "READY!"
    status_timer: float = 1.0
    event_score_text: str = ""
    event_score_timer: float = 0.0
    rng: random.Random = field(
        default_factory=lambda: random.Random(31),
        repr=False,
    )
    particles: ProceduralParticleEmitterState = field(
        default_factory=ProceduralParticleEmitterState,
        repr=False,
    )

    def remaining_collectibles(self) -> int:
        return len(self.collectibles.items)

    def reset_collectibles(self) -> None:
        self.collectibles = CollectibleField(
            items={
                coord: CollectibleState(kind=kind)
                for coord, kind in self.collectible_blueprint
            }
        )

    def reset_positions(self) -> None:
        self.player.cell = self.player_start
        self.player.direction = self.player_start_direction
        self.player.pending_direction = None
        self.player.moved_this_frame = 0
        for ghost in self.ghosts:
            ghost.reset()

    def reset_round_state(self) -> None:
        self.reset_positions()
        self.mode_timer = ModeTimerState()
        clear_timed_state(self.frightened)
        reset_score_chain(self.ghost_chain)
        self.freeze_timer = 1.0
        self.flash_timer = 0.0
        self.effect_timer = 0.0
        self.effect_intensity = 0.0
        self.status_text = "READY!"
        self.status_timer = 1.0
        self.event_score_text = ""
        self.event_score_timer = 0.0

    def round_active(self) -> bool:
        return not self.game_over and not self.victory and self.lives > 0


@dataclass(frozen=True)
class PlayIntent(BaseIntent):
    move_up: bool = False
    move_down: bool = False
    move_left: bool = False
    move_right: bool = False
    confirm: bool = False
    pause: bool = False


@dataclass
class PlayTickContext(BaseTickContext[PlayWorld, PlayIntent]):
    pass
