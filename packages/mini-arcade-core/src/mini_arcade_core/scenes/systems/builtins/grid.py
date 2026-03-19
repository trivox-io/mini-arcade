"""
Reusable grid/discrete-step gameplay helpers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, Iterable, Optional, TypeVar, Union

from mini_arcade_core.engine.entities import BaseEntity
from mini_arcade_core.scenes.systems.phases import SystemPhase

# pylint: disable=invalid-name
TCtx = TypeVar("TCtx")
SpawnResult = Optional[Union[BaseEntity, Iterable[BaseEntity]]]
CadenceInterval = Union[float, Callable[[TCtx], float]]
# pylint: enable=invalid-name


def _default_enabled_when(_ctx: object) -> bool:
    return True


def _normalize_spawned(spawned: SpawnResult) -> tuple[BaseEntity, ...]:
    if spawned is None:
        return ()
    if isinstance(spawned, BaseEntity):
        return (spawned,)
    return tuple(entity for entity in spawned if entity is not None)


@dataclass(frozen=True, order=True)
class GridCoord:
    """
    One integer grid cell coordinate.
    """

    col: int
    row: int

    def translated(self, *, dcol: int = 0, drow: int = 0) -> "GridCoord":
        """
        Return a new cell translated by integer deltas.
        """

        return GridCoord(
            col=int(self.col) + int(dcol), row=int(self.row) + int(drow)
        )


@dataclass(frozen=True)
class GridBounds:
    """
    Rectangular grid bounds measured in cells.
    """

    cols: int
    rows: int

    def contains(self, coord: GridCoord) -> bool:
        """
        Return whether a cell lies inside this grid.
        """

        return 0 <= int(coord.col) < int(self.cols) and 0 <= int(
            coord.row
        ) < int(self.rows)

    def iter_cells(self) -> tuple[GridCoord, ...]:
        """
        Return every cell inside the bounds in row-major order.
        """

        return tuple(
            GridCoord(col=col, row=row)
            for row in range(int(self.rows))
            for col in range(int(self.cols))
        )


@dataclass(frozen=True)
class GridLayout:
    """
    World-space layout for a rectangular cell grid.
    """

    bounds: GridBounds
    cell_width: float
    cell_height: float
    origin_x: float = 0.0
    origin_y: float = 0.0

    def cell_origin(self, coord: GridCoord) -> tuple[float, float]:
        """
        Return the top-left world coordinate for a grid cell.
        """

        return (
            float(self.origin_x) + (int(coord.col) * float(self.cell_width)),
            float(self.origin_y) + (int(coord.row) * float(self.cell_height)),
        )

    def cell_center(self, coord: GridCoord) -> tuple[float, float]:
        """
        Return the center world coordinate for a grid cell.
        """

        x, y = self.cell_origin(coord)
        return (
            x + (float(self.cell_width) * 0.5),
            y + (float(self.cell_height) * 0.5),
        )

    def cell_rect(self, coord: GridCoord) -> tuple[float, float, float, float]:
        """
        Return a world-space rect tuple `(x, y, w, h)` for a grid cell.
        """

        x, y = self.cell_origin(coord)
        return (x, y, float(self.cell_width), float(self.cell_height))

    def contains(self, coord: GridCoord) -> bool:
        """
        Delegate containment checks to bounds.
        """

        return self.bounds.contains(coord)


def occupied_grid_cells(
    values: Iterable[object],
    *,
    coord_getter: Callable[[object], GridCoord | None],
    include: Callable[[object], bool] | None = None,
) -> set[GridCoord]:
    """
    Collect occupied cells from arbitrary values.
    """

    out: set[GridCoord] = set()
    include = include or (lambda _value: True)
    for value in values:
        if not include(value):
            continue
        coord = coord_getter(value)
        if coord is None:
            continue
        out.add(coord)
    return out


def free_grid_cells(
    bounds: GridBounds,
    occupied: Iterable[GridCoord],
) -> tuple[GridCoord, ...]:
    """
    Return free cells inside `bounds` after subtracting occupied cells.
    """

    blocked = {coord for coord in occupied if bounds.contains(coord)}
    return tuple(
        coord for coord in bounds.iter_cells() if coord not in blocked
    )


def choose_first_grid_cell(
    _ctx: object,
    cells: tuple[GridCoord, ...],
) -> GridCoord | None:
    """
    Deterministic default cell chooser.
    """

    return cells[0] if cells else None


@dataclass
class CadenceState:
    """
    Mutable state for fixed-interval gameplay stepping.
    """

    accumulator: float = 0.0
    tick_count: int = 0
    steps_this_frame: int = 0


@dataclass(frozen=True)
class CadenceBinding(Generic[TCtx]):
    """
    Declarative fixed-cadence simulation rule.
    """

    state_getter: Callable[[TCtx], CadenceState]
    interval_seconds: CadenceInterval
    on_tick: Callable[[TCtx], None]
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    max_steps_per_frame: int = 4


@dataclass
class CadenceSystem(Generic[TCtx]):
    """
    Execute one or more fixed-timestep callbacks from variable frame dt.
    """

    name: str = "common_cadence"
    phase: int = SystemPhase.SIMULATION
    order: int = 20
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    bindings: tuple[CadenceBinding[TCtx], ...] = ()

    def step(self, ctx: TCtx) -> None:
        """Advance cadence timers and fire callbacks when they elapse."""

        if not self.enabled_when(ctx):
            return

        frame_dt = max(0.0, float(getattr(ctx, "dt", 0.0)))
        if frame_dt <= 0.0:
            return

        for binding in self.bindings:
            state = binding.state_getter(ctx)
            state.steps_this_frame = 0
            if not binding.enabled_when(ctx):
                continue

            interval_value = binding.interval_seconds
            if callable(interval_value):
                interval_value = interval_value(ctx)
            interval = max(0.0001, float(interval_value))
            state.accumulator += frame_dt

            while (
                state.accumulator >= interval
                and state.steps_this_frame < int(binding.max_steps_per_frame)
            ):
                state.accumulator -= interval
                state.steps_this_frame += 1
                state.tick_count += 1
                binding.on_tick(ctx)


@dataclass(frozen=True)
class GridCellSpawnBinding(Generic[TCtx]):
    """
    Declarative spawn rule that chooses one currently free cell in a grid.
    """

    should_spawn: Callable[[TCtx], bool]
    bounds_getter: Callable[[TCtx], GridBounds]
    occupied_cells_getter: Callable[[TCtx], Iterable[GridCoord]]
    spawn: Callable[[TCtx, GridCoord], SpawnResult]
    choose_cell: Callable[[TCtx, tuple[GridCoord, ...]], GridCoord | None] = (
        choose_first_grid_cell
    )
    on_spawned: (
        Callable[[TCtx, tuple[BaseEntity, ...], GridCoord], None] | None
    ) = None
    insert_into_world: bool = True


@dataclass
class GridCellSpawnSystem(Generic[TCtx]):
    """
    Spawn entities into currently free grid cells.
    """

    name: str = "common_grid_spawn"
    phase: int = SystemPhase.SIMULATION
    order: int = 25
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    bindings: tuple[GridCellSpawnBinding[TCtx], ...] = ()

    def step(self, ctx: TCtx) -> None:
        """Spawn entities into the first available grid cell per binding."""

        if not self.enabled_when(ctx):
            return

        for binding in self.bindings:
            if not binding.should_spawn(ctx):
                continue

            bounds = binding.bounds_getter(ctx)
            free_cells = free_grid_cells(
                bounds,
                binding.occupied_cells_getter(ctx),
            )
            if not free_cells:
                continue

            cell = binding.choose_cell(ctx, free_cells)
            if cell is None or cell not in free_cells:
                continue

            spawned = _normalize_spawned(binding.spawn(ctx, cell))
            if not spawned:
                continue

            if binding.insert_into_world:
                ctx.world.entities.extend(spawned)
            if binding.on_spawned is not None:
                binding.on_spawned(ctx, spawned, cell)


__all__ = [
    "CadenceBinding",
    "CadenceState",
    "CadenceSystem",
    "GridBounds",
    "GridCellSpawnBinding",
    "GridCellSpawnSystem",
    "GridCoord",
    "GridLayout",
    "choose_first_grid_cell",
    "free_grid_cells",
    "occupied_grid_cells",
]
