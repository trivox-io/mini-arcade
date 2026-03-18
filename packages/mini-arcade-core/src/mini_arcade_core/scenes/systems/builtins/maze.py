"""
Reusable maze and lane-based grid gameplay helpers.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Generic, Iterable, Mapping, TypeVar

from mini_arcade_core.scenes.systems.builtins.grid import GridBounds, GridCoord
from mini_arcade_core.scenes.systems.phases import SystemPhase

# pylint: disable=invalid-name
TCtx = TypeVar("TCtx")
TCell = TypeVar("TCell")
# pylint: enable=invalid-name


def _default_enabled_when(_ctx: object) -> bool:
    return True


class CardinalDirection(str, Enum):
    """
    Four-way grid direction.
    """

    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"

    @property
    def vector(self) -> tuple[int, int]:
        """Return the `(dcol, drow)` vector for this direction."""

        if self is CardinalDirection.UP:
            return (0, -1)
        if self is CardinalDirection.DOWN:
            return (0, 1)
        if self is CardinalDirection.LEFT:
            return (-1, 0)
        return (1, 0)

    @property
    def opposite(self) -> "CardinalDirection":
        """Return the opposite cardinal direction."""

        if self is CardinalDirection.UP:
            return CardinalDirection.DOWN
        if self is CardinalDirection.DOWN:
            return CardinalDirection.UP
        if self is CardinalDirection.LEFT:
            return CardinalDirection.RIGHT
        return CardinalDirection.LEFT


def step_in_direction(
    coord: GridCoord,
    direction: CardinalDirection,
) -> GridCoord:
    """
    Return the adjacent cell in the given direction.
    """

    dcol, drow = direction.vector
    return coord.translated(dcol=dcol, drow=drow)


@dataclass
class TileMap(Generic[TCell]):
    """
    Dense grid of maze/tile values.
    """

    bounds: GridBounds
    default: TCell | None = None
    _cells: list[list[TCell | None]] = field(
        default_factory=list,
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        self._cells = [
            [self.default for _ in range(int(self.bounds.cols))]
            for _ in range(int(self.bounds.rows))
        ]

    def contains(self, coord: GridCoord) -> bool:
        """Return whether a coordinate falls inside the tile-map bounds."""

        return self.bounds.contains(coord)

    def get(self, coord: GridCoord) -> TCell | None:
        """Return the stored tile value at one coordinate, if in bounds."""

        if not self.contains(coord):
            return None
        return self._cells[int(coord.row)][int(coord.col)]

    def set(self, coord: GridCoord, value: TCell | None) -> None:
        """Store a tile value at one coordinate."""

        if not self.contains(coord):
            raise IndexError(f"Cell out of bounds: {coord!r}")
        self._cells[int(coord.row)][int(coord.col)] = value

    def iter_cells(self) -> tuple[tuple[GridCoord, TCell | None], ...]:
        """
        Return all cells with their stored values.
        """

        return tuple(
            (
                GridCoord(col=col, row=row),
                self._cells[row][col],
            )
            for row in range(int(self.bounds.rows))
            for col in range(int(self.bounds.cols))
        )


def tile_map_from_strings(
    *rows: str,
    legend: Mapping[str, TCell],
    default: TCell | None = None,
) -> TileMap[TCell]:
    """
    Build a tile map from ASCII rows and a legend.
    """

    width = max((len(row) for row in rows), default=0)
    tile_map = TileMap[TCell](
        bounds=GridBounds(cols=width, rows=len(rows)),
        default=default,
    )
    for row_idx, row in enumerate(rows):
        for col_idx, char in enumerate(row):
            if char in legend:
                tile_map.set(
                    GridCoord(col=col_idx, row=row_idx),
                    legend[char],
                )
    return tile_map


def available_directions(
    tile_map: TileMap[TCell],
    coord: GridCoord,
    *,
    can_enter: Callable[[TCell | None], bool],
) -> tuple[CardinalDirection, ...]:
    """
    Return the cardinal exits available from one cell.
    """

    out: list[CardinalDirection] = []
    for direction in CardinalDirection:
        target = step_in_direction(coord, direction)
        if not tile_map.contains(target):
            continue
        if can_enter(tile_map.get(target)):
            out.append(direction)
    return tuple(out)


def _filtered_directions(
    directions: tuple[CardinalDirection, ...],
    *,
    current_direction: CardinalDirection | None,
    allow_reverse: bool,
) -> tuple[CardinalDirection, ...]:
    if allow_reverse or current_direction is None:
        return directions

    non_reverse = tuple(
        direction
        for direction in directions
        if direction is not current_direction.opposite
    )
    return non_reverse or directions


def choose_direction_toward(
    tile_map: TileMap[TCell],
    coord: GridCoord,
    target: GridCoord,
    *,
    can_enter: Callable[[TCell | None], bool],
    current_direction: CardinalDirection | None = None,
    allow_reverse: bool = False,
) -> CardinalDirection | None:
    """
    Choose the exit that minimizes Manhattan distance to a target cell.
    """

    exits = _filtered_directions(
        available_directions(tile_map, coord, can_enter=can_enter),
        current_direction=current_direction,
        allow_reverse=allow_reverse,
    )
    if not exits:
        return None

    return min(
        exits,
        key=lambda direction: (
            abs(step_in_direction(coord, direction).col - target.col)
            + abs(step_in_direction(coord, direction).row - target.row),
            direction.value,
        ),
    )


def choose_direction_away(
    tile_map: TileMap[TCell],
    coord: GridCoord,
    target: GridCoord,
    *,
    can_enter: Callable[[TCell | None], bool],
    current_direction: CardinalDirection | None = None,
    allow_reverse: bool = False,
) -> CardinalDirection | None:
    """
    Choose the exit that maximizes Manhattan distance from a target cell.
    """

    exits = _filtered_directions(
        available_directions(tile_map, coord, can_enter=can_enter),
        current_direction=current_direction,
        allow_reverse=allow_reverse,
    )
    if not exits:
        return None

    return max(
        exits,
        key=lambda direction: (
            abs(step_in_direction(coord, direction).col - target.col)
            + abs(step_in_direction(coord, direction).row - target.row),
            direction.value,
        ),
    )


def choose_random_direction(
    tile_map: TileMap[TCell],
    coord: GridCoord,
    *,
    can_enter: Callable[[TCell | None], bool],
    rng: random.Random | None = None,
    current_direction: CardinalDirection | None = None,
    allow_reverse: bool = False,
) -> CardinalDirection | None:
    """
    Choose one valid exit randomly.
    """

    exits = _filtered_directions(
        available_directions(tile_map, coord, can_enter=can_enter),
        current_direction=current_direction,
        allow_reverse=allow_reverse,
    )
    if not exits:
        return None

    chooser = rng or random.Random(1)
    return chooser.choice(exits)


def is_junction(
    tile_map: TileMap[TCell],
    coord: GridCoord,
    *,
    can_enter: Callable[[TCell | None], bool],
) -> bool:
    """
    Return whether a cell exposes more than two valid exits.
    """

    return len(available_directions(tile_map, coord, can_enter=can_enter)) >= 3


@dataclass
class GridNavigatorState:
    """
    Mutable cell-based movement state for one maze agent.
    """

    cell: GridCoord
    direction: CardinalDirection
    pending_direction: CardinalDirection | None = None
    moved_this_frame: int = 0


@dataclass(frozen=True)
class GridNavigationBinding(Generic[TCtx, TCell]):
    """
    Declarative lane/junction navigation rule.
    """

    state_getter: Callable[[TCtx], GridNavigatorState]
    tile_map_getter: Callable[[TCtx], TileMap[TCell]]
    desired_direction_getter: Callable[[TCtx], CardinalDirection | None] = (
        lambda _ctx: None
    )
    can_enter: Callable[[TCell | None], bool] = lambda value: value is not None
    on_cell_entered: Callable[[TCtx, GridCoord], None] | None = None
    allow_reverse: bool = True
    steps_getter: Callable[[TCtx], int] = lambda _ctx: 1


@dataclass
class GridNavigationSystem(Generic[TCtx, TCell]):
    """
    Advance one or more maze agents through a tile map with turn buffering.
    """

    name: str = "common_grid_navigation"
    phase: int = SystemPhase.SIMULATION
    order: int = 30
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    bindings: tuple[GridNavigationBinding[TCtx, TCell], ...] = ()

    def step(self, ctx: TCtx) -> None:
        """Advance bound navigators through the tile map with turn buffering."""

        if not self.enabled_when(ctx):
            return

        for binding in self.bindings:
            state = binding.state_getter(ctx)
            tile_map = binding.tile_map_getter(ctx)
            requested = binding.desired_direction_getter(ctx)
            if requested is not None:
                if (
                    binding.allow_reverse
                    or requested != state.direction.opposite
                ):
                    state.pending_direction = requested

            state.moved_this_frame = 0
            for _ in range(max(0, int(binding.steps_getter(ctx)))):
                exits = available_directions(
                    tile_map,
                    state.cell,
                    can_enter=binding.can_enter,
                )

                next_direction = state.direction
                if state.pending_direction in exits:
                    next_direction = state.pending_direction
                    state.pending_direction = None
                elif next_direction not in exits:
                    break

                state.direction = next_direction
                state.cell = step_in_direction(state.cell, next_direction)
                state.moved_this_frame += 1
                if binding.on_cell_entered is not None:
                    binding.on_cell_entered(ctx, state.cell)


@dataclass(frozen=True)
class TunnelWrapBinding(Generic[TCtx]):
    """
    Declarative horizontal/vertical wrap rule for maze agents.
    """

    states_getter: Callable[[TCtx], Iterable[GridNavigatorState]]
    bounds_getter: Callable[[TCtx], GridBounds]
    wrap_horizontal: bool = True
    wrap_vertical: bool = False


@dataclass
class TunnelWrapSystem(Generic[TCtx]):
    """
    Wrap maze agents across configured grid edges.
    """

    name: str = "common_tunnel_wrap"
    phase: int = SystemPhase.SIMULATION
    order: int = 31
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    bindings: tuple[TunnelWrapBinding[TCtx], ...] = ()

    def step(self, ctx: TCtx) -> None:
        """Wrap navigator states across configured map edges."""

        if not self.enabled_when(ctx):
            return

        for binding in self.bindings:
            bounds = binding.bounds_getter(ctx)
            for state in binding.states_getter(ctx):
                if binding.wrap_horizontal:
                    if int(state.cell.col) < 0:
                        state.cell = GridCoord(
                            col=int(bounds.cols) - 1,
                            row=int(state.cell.row),
                        )
                    elif int(state.cell.col) >= int(bounds.cols):
                        state.cell = GridCoord(
                            col=0,
                            row=int(state.cell.row),
                        )
                if binding.wrap_vertical:
                    if int(state.cell.row) < 0:
                        state.cell = GridCoord(
                            col=int(state.cell.col),
                            row=int(bounds.rows) - 1,
                        )
                    elif int(state.cell.row) >= int(bounds.rows):
                        state.cell = GridCoord(
                            col=int(state.cell.col),
                            row=0,
                        )


class CollectibleKind(str, Enum):
    """
    Common collectible kinds for maze games.
    """

    PELLET = "pellet"
    POWER = "power"
    BONUS = "bonus"


@dataclass
class CollectibleState:
    """
    Mutable collectible metadata stored inside a field.
    """

    kind: CollectibleKind
    payload: Any = None


@dataclass
class CollectibleField:
    """
    Dense collectible state keyed by grid cell.
    """

    items: dict[GridCoord, CollectibleState] = field(default_factory=dict)

    def item_at(self, coord: GridCoord) -> CollectibleState | None:
        """Return the collectible stored at one cell, if any."""

        return self.items.get(coord)

    def occupied_cells(self) -> tuple[GridCoord, ...]:
        """Return the cells that currently contain collectibles."""

        return tuple(self.items.keys())

    def remove(self, coord: GridCoord) -> CollectibleState | None:
        """Remove and return the collectible stored at one cell."""

        return self.items.pop(coord, None)


@dataclass(frozen=True)
class CollectibleCollisionBinding(Generic[TCtx]):
    """
    Declarative collectible pickup rule.
    """

    collector_cell_getter: Callable[[TCtx], GridCoord]
    field_getter: Callable[[TCtx], CollectibleField | None]
    on_collect: Callable[[TCtx, GridCoord, CollectibleState], None] | None = (
        None
    )


@dataclass
class CollectibleCollisionSystem(Generic[TCtx]):
    """
    Consume collectibles when a collector enters the same cell.
    """

    name: str = "common_collectible_collision"
    phase: int = SystemPhase.SIMULATION
    order: int = 35
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    bindings: tuple[CollectibleCollisionBinding[TCtx], ...] = ()

    def step(self, ctx: TCtx) -> None:
        """Consume collectibles that share a cell with the collector."""

        if not self.enabled_when(ctx):
            return

        for binding in self.bindings:
            collectible_field = binding.field_getter(ctx)
            if collectible_field is None:
                continue
            coord = binding.collector_cell_getter(ctx)
            item = collectible_field.remove(coord)
            if item is None:
                continue
            if binding.on_collect is not None:
                binding.on_collect(ctx, coord, item)


@dataclass(frozen=True)
class TimedMode:
    """
    One timed gameplay mode segment.
    """

    name: str
    duration_seconds: float | None
    payload: Any = None


@dataclass
class ModeTimerState:
    """
    Mutable state for timed mode progression.
    """

    mode_index: int = 0
    elapsed_in_mode: float = 0.0
    current_mode: str = ""


@dataclass(frozen=True)
class ModeTimerBinding(Generic[TCtx]):
    """
    Declarative timed mode schedule.
    """

    state_getter: Callable[[TCtx], ModeTimerState]
    schedule: tuple[TimedMode, ...]
    on_mode_changed: Callable[[TCtx, TimedMode], None] | None = None
    loop: bool = False


@dataclass
class ModeTimerSystem(Generic[TCtx]):
    """
    Advance timed mode schedules using the current frame dt.
    """

    name: str = "common_mode_timer"
    phase: int = SystemPhase.SIMULATION
    order: int = 15
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    bindings: tuple[ModeTimerBinding[TCtx], ...] = ()

    def step(self, ctx: TCtx) -> None:
        """Advance scheduled timed modes using the current frame delta."""

        if not self.enabled_when(ctx):
            return

        dt = max(0.0, float(getattr(ctx, "dt", 0.0)))
        if dt <= 0.0:
            return

        for binding in self.bindings:
            if not binding.schedule:
                continue
            state = binding.state_getter(ctx)
            if not state.current_mode:
                first = binding.schedule[0]
                state.current_mode = first.name
                if binding.on_mode_changed is not None:
                    binding.on_mode_changed(ctx, first)

            state.elapsed_in_mode += dt
            while True:
                current = binding.schedule[state.mode_index]
                if current.duration_seconds is None:
                    break
                if state.elapsed_in_mode < float(current.duration_seconds):
                    break

                state.elapsed_in_mode -= float(current.duration_seconds)
                next_index = state.mode_index + 1
                if next_index >= len(binding.schedule):
                    if not binding.loop:
                        state.mode_index = len(binding.schedule) - 1
                        state.current_mode = binding.schedule[
                            state.mode_index
                        ].name
                        state.elapsed_in_mode = 0.0
                        break
                    next_index = 0

                state.mode_index = next_index
                next_mode = binding.schedule[state.mode_index]
                state.current_mode = next_mode.name
                if binding.on_mode_changed is not None:
                    binding.on_mode_changed(ctx, next_mode)


__all__ = [
    "CardinalDirection",
    "CollectibleCollisionBinding",
    "CollectibleCollisionSystem",
    "CollectibleField",
    "CollectibleKind",
    "CollectibleState",
    "GridNavigationBinding",
    "GridNavigationSystem",
    "GridNavigatorState",
    "ModeTimerBinding",
    "ModeTimerState",
    "ModeTimerSystem",
    "TimedMode",
    "TileMap",
    "TunnelWrapBinding",
    "TunnelWrapSystem",
    "available_directions",
    "choose_direction_away",
    "choose_direction_toward",
    "choose_random_direction",
    "is_junction",
    "step_in_direction",
    "tile_map_from_strings",
]
