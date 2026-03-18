from __future__ import annotations

from dataclasses import dataclass, field

from mini_arcade_core.engine.commands import ChangeSceneCommand
from mini_arcade_core.scenes.systems.base_system import BaseSystem
from mini_arcade_core.scenes.systems.builtins import (
    CadenceBinding,
    CadenceSystem,
    CardinalDirection,
    CollectibleCollisionBinding,
    CollectibleCollisionSystem,
    CollectibleKind,
    CollectibleState,
    GridCoord,
    GridNavigationBinding,
    GridNavigationSystem,
    ModeTimerBinding,
    ModeTimerSystem,
    ScoreChainBinding,
    ScoreChainSystem,
    TimedMode,
    TimedState,
    TimedStateBinding,
    TimedStateSystem,
    activate_timed_state,
    choose_direction_away,
    choose_direction_toward,
    choose_random_direction,
    claim_score_chain_points,
    reset_score_chain,
)
from mini_arcade_core.scenes.systems.phases import SystemPhase

from ..models import GhostState, PlayIntent, PlayTickContext

PLAYER_STEP_SECONDS = 0.11
GHOST_STEP_SECONDS = 0.125
PELLET_SCORE = 10
POWER_SCORE = 50
FRIGHTENED_SECONDS = 6.0
GHOST_CHAIN_STEPS = (200, 400, 800, 1600)
FLASH_SECONDS = 0.18
EFFECT_SECONDS = 0.24

MODE_SCHEDULE = (
    TimedMode(name="scatter", duration_seconds=7.0),
    TimedMode(name="chase", duration_seconds=10.0),
    TimedMode(name="scatter", duration_seconds=7.0),
    TimedMode(name="chase", duration_seconds=12.0),
    TimedMode(name="chase", duration_seconds=None),
)


def _can_enter(tile: str | None) -> bool:
    return tile == "lane"


def _simulation_enabled(ctx: PlayTickContext) -> bool:
    return ctx.world.round_active() and ctx.world.freeze_timer <= 0.0


def _refresh_best_score(ctx: PlayTickContext) -> None:
    ctx.world.best_score = max(ctx.world.best_score, ctx.world.score)


def _intent_direction(intent: PlayIntent | None) -> CardinalDirection | None:
    if intent is None:
        return None
    if intent.move_up:
        return CardinalDirection.UP
    if intent.move_down:
        return CardinalDirection.DOWN
    if intent.move_left:
        return CardinalDirection.LEFT
    if intent.move_right:
        return CardinalDirection.RIGHT
    return None


def _set_event(
    ctx: PlayTickContext,
    *,
    cell: GridCoord,
    flash_color: tuple[int, int, int],
    score_text: str = "",
    intensity: float = 1.0,
) -> None:
    world = ctx.world
    world.effect_origin = world.layout.cell_center(cell)
    world.effect_timer = EFFECT_SECONDS
    world.effect_intensity = intensity
    world.flash_color = flash_color
    world.flash_timer = FLASH_SECONDS
    world.event_score_text = score_text
    world.event_score_timer = 0.75 if score_text else 0.0


def _step_feedback(ctx: PlayTickContext) -> None:
    world = ctx.world
    world.freeze_timer = max(0.0, world.freeze_timer - ctx.dt)
    world.flash_timer = max(0.0, world.flash_timer - ctx.dt)
    world.effect_timer = max(0.0, world.effect_timer - ctx.dt)
    world.event_score_timer = max(0.0, world.event_score_timer - ctx.dt)
    if world.event_score_timer <= 0.0:
        world.event_score_text = ""
    world.status_timer = max(0.0, world.status_timer - ctx.dt)
    if world.status_timer <= 0.0 and world.status_text not in {
        "GAME OVER",
        "MAZE CLEAR",
    }:
        world.status_text = ""


def _advance_target(
    origin: GridCoord,
    direction: CardinalDirection,
    steps: int,
) -> GridCoord:
    out = origin
    for _ in range(max(0, int(steps))):
        dcol, drow = direction.vector
        out = out.translated(dcol=dcol, drow=drow)
    return out


def _manhattan(a: GridCoord, b: GridCoord) -> int:
    return abs(int(a.col) - int(b.col)) + abs(int(a.row) - int(b.row))


def _ghost_target_direction(
    ctx: PlayTickContext,
    ghost: GhostState,
) -> CardinalDirection | None:
    world = ctx.world
    if ghost.eaten:
        return choose_direction_toward(
            world.tile_map,
            ghost.navigator.cell,
            ghost.spawn_cell,
            can_enter=_can_enter,
            current_direction=ghost.navigator.direction,
            allow_reverse=True,
        )

    if world.frightened.active:
        return choose_random_direction(
            world.tile_map,
            ghost.navigator.cell,
            can_enter=_can_enter,
            rng=world.rng,
            current_direction=ghost.navigator.direction,
        )

    mode = world.mode_timer.current_mode or "scatter"
    player_cell = world.player.cell
    if mode == "scatter":
        target = ghost.scatter_target
    elif ghost.name == "B":
        target = player_cell
    elif ghost.name == "I":
        target = _advance_target(player_cell, world.player.direction, 2)
    elif ghost.name == "K":
        target = _advance_target(player_cell, world.player.direction, 4)
    else:
        if _manhattan(ghost.navigator.cell, player_cell) <= 4:
            return choose_direction_away(
                world.tile_map,
                ghost.navigator.cell,
                player_cell,
                can_enter=_can_enter,
                current_direction=ghost.navigator.direction,
            )
        target = player_cell

    return choose_direction_toward(
        world.tile_map,
        ghost.navigator.cell,
        target,
        can_enter=_can_enter,
        current_direction=ghost.navigator.direction,
    )


def _on_mode_changed(ctx: PlayTickContext, mode: TimedMode) -> None:
    if ctx.world.frightened.active:
        return
    ctx.world.status_text = mode.name.upper()
    ctx.world.status_timer = 0.45


def _on_frightened_expired(
    ctx: PlayTickContext,
    _state: TimedState,
) -> None:
    reset_score_chain(ctx.world.ghost_chain)
    ctx.world.status_text = "CHASE"
    ctx.world.status_timer = 0.45


def _lose_life(ctx: PlayTickContext) -> None:
    world = ctx.world
    world.lives -= 1
    if world.lives <= 0:
        world.lives = 0
        world.game_over = True
        world.status_text = "GAME OVER"
        world.status_timer = 99.0
        world.freeze_timer = 0.0
        return

    world.reset_round_state()


def _handle_collectible(
    ctx: PlayTickContext,
    coord: GridCoord,
    item: CollectibleState,
) -> None:
    world = ctx.world

    if item.kind is CollectibleKind.PELLET:
        world.score += PELLET_SCORE
        _set_event(
            ctx,
            cell=coord,
            flash_color=(68, 76, 124),
            intensity=0.55,
        )
    elif item.kind is CollectibleKind.POWER:
        world.score += POWER_SCORE
        activate_timed_state(
            world.frightened,
            duration_seconds=FRIGHTENED_SECONDS,
            tag="frightened",
        )
        reset_score_chain(world.ghost_chain)
        world.status_text = "POWER!"
        world.status_timer = 0.65
        for ghost in world.ghosts:
            if ghost.eaten:
                continue
            ghost.navigator.pending_direction = (
                ghost.navigator.direction.opposite
            )
        _set_event(
            ctx,
            cell=coord,
            flash_color=(72, 104, 255),
            score_text="50",
            intensity=1.25,
        )

    _refresh_best_score(ctx)
    if world.remaining_collectibles() <= 0:
        world.victory = True
        world.status_text = "MAZE CLEAR"
        world.status_timer = 99.0
        world.freeze_timer = 0.0


def _resolve_player_ghost_overlap(ctx: PlayTickContext) -> bool:
    world = ctx.world
    player_cell = world.player.cell
    for ghost in world.ghosts:
        if ghost.navigator.cell != player_cell or ghost.eaten:
            continue

        if world.frightened.active:
            ghost.eaten = True
            points = claim_score_chain_points(
                world.ghost_chain,
                steps=GHOST_CHAIN_STEPS,
                window_seconds=max(
                    0.4,
                    world.frightened.remaining_seconds,
                ),
            )
            world.score += int(points)
            _refresh_best_score(ctx)
            world.status_text = f"{points}!"
            world.status_timer = 0.55
            _set_event(
                ctx,
                cell=ghost.navigator.cell,
                flash_color=(255, 255, 255),
                score_text=str(points),
                intensity=1.5,
            )
            return False

        _lose_life(ctx)
        return True
    return False


@dataclass
class PlayRulesSystem(BaseSystem[PlayTickContext]):
    name: str = "play_rules"
    phase: int = SystemPhase.SIMULATION
    order: int = 20
    _mode_timer: ModeTimerSystem[PlayTickContext] = field(
        init=False,
        repr=False,
    )
    _frightened_timer: TimedStateSystem[PlayTickContext] = field(
        init=False,
        repr=False,
    )
    _ghost_chain_timer: ScoreChainSystem[PlayTickContext] = field(
        init=False,
        repr=False,
    )
    _player_navigation: GridNavigationSystem[PlayTickContext, str] = field(
        init=False,
        repr=False,
    )
    _ghost_navigation: GridNavigationSystem[PlayTickContext, str] = field(
        init=False,
        repr=False,
    )
    _collectibles: CollectibleCollisionSystem[PlayTickContext] = field(
        init=False,
        repr=False,
    )
    _player_cadence: CadenceSystem[PlayTickContext] = field(
        init=False,
        repr=False,
    )
    _ghost_cadence: CadenceSystem[PlayTickContext] = field(
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        self._mode_timer = ModeTimerSystem(
            enabled_when=_simulation_enabled,
            bindings=(
                ModeTimerBinding(
                    state_getter=lambda ctx: ctx.world.mode_timer,
                    schedule=MODE_SCHEDULE,
                    on_mode_changed=_on_mode_changed,
                ),
            ),
        )
        self._frightened_timer = TimedStateSystem(
            bindings=(
                TimedStateBinding(
                    state_getter=lambda ctx: ctx.world.frightened,
                    on_expired=_on_frightened_expired,
                ),
            )
        )
        self._ghost_chain_timer = ScoreChainSystem(
            bindings=(
                ScoreChainBinding(
                    state_getter=lambda ctx: ctx.world.ghost_chain,
                ),
            )
        )
        self._player_navigation = GridNavigationSystem(
            bindings=(
                GridNavigationBinding(
                    state_getter=lambda ctx: ctx.world.player,
                    tile_map_getter=lambda ctx: ctx.world.tile_map,
                    desired_direction_getter=lambda ctx: _intent_direction(
                        ctx.intent
                    ),
                    can_enter=_can_enter,
                    allow_reverse=True,
                ),
            )
        )

        ghost_bindings: list[GridNavigationBinding[PlayTickContext, str]] = []
        for index in range(4):
            ghost_bindings.append(
                GridNavigationBinding(
                    state_getter=lambda ctx, i=index: ctx.world.ghosts[
                        i
                    ].navigator,
                    tile_map_getter=lambda ctx: ctx.world.tile_map,
                    desired_direction_getter=lambda ctx, i=index: ctx.world.ghosts[
                        i
                    ].desired_direction,
                    can_enter=_can_enter,
                    allow_reverse=False,
                )
            )
        self._ghost_navigation = GridNavigationSystem(
            bindings=tuple(ghost_bindings)
        )

        self._collectibles = CollectibleCollisionSystem(
            bindings=(
                CollectibleCollisionBinding(
                    collector_cell_getter=lambda ctx: ctx.world.player.cell,
                    field_getter=lambda ctx: ctx.world.collectibles,
                    on_collect=_handle_collectible,
                ),
            )
        )
        self._player_cadence = CadenceSystem(
            bindings=(
                CadenceBinding(
                    state_getter=lambda ctx: ctx.world.player_cadence,
                    interval_seconds=PLAYER_STEP_SECONDS,
                    on_tick=self._step_player,
                    enabled_when=_simulation_enabled,
                ),
            )
        )
        self._ghost_cadence = CadenceSystem(
            bindings=(
                CadenceBinding(
                    state_getter=lambda ctx: ctx.world.ghost_cadence,
                    interval_seconds=GHOST_STEP_SECONDS,
                    on_tick=self._step_ghosts,
                    enabled_when=_simulation_enabled,
                ),
            )
        )

    def _step_player(self, ctx: PlayTickContext) -> None:
        self._player_navigation.step(ctx)
        self._collectibles.step(ctx)
        _resolve_player_ghost_overlap(ctx)

    def _step_ghosts(self, ctx: PlayTickContext) -> None:
        for ghost in ctx.world.ghosts:
            ghost.desired_direction = _ghost_target_direction(ctx, ghost)

        self._ghost_navigation.step(ctx)

        for ghost in ctx.world.ghosts:
            if ghost.eaten and ghost.navigator.cell == ghost.spawn_cell:
                ghost.eaten = False
                ghost.navigator.direction = ghost.start_direction
                ghost.navigator.pending_direction = None

        _resolve_player_ghost_overlap(ctx)

    def step(self, ctx: PlayTickContext):
        _step_feedback(ctx)

        if (
            ctx.intent is not None
            and ctx.intent.confirm
            and (ctx.world.game_over or ctx.world.victory)
        ):
            ctx.commands.push(ChangeSceneCommand("play"))
            return

        self._mode_timer.step(ctx)
        self._frightened_timer.step(ctx)
        self._ghost_chain_timer.step(ctx)
        self._player_cadence.step(ctx)
        self._ghost_cadence.step(ctx)
