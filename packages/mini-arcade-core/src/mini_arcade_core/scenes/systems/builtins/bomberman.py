"""
Reusable arena bomb/explosion helpers for Bomberman-style games.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Generic, Iterable, TypeVar

from mini_arcade_core.scenes.systems.builtins.grid import GridCoord
from mini_arcade_core.scenes.systems.builtins.maze import (
    CardinalDirection,
    TileMap,
    step_in_direction,
    tile_map_from_strings,
)
from mini_arcade_core.scenes.systems.phases import SystemPhase

# pylint: disable=invalid-name
TCtx = TypeVar("TCtx")
# pylint: enable=invalid-name


def _default_enabled_when(_ctx: object) -> bool:
    return True


class ArenaTile(str, Enum):
    """
    Common arena tile kinds for bomb-based grid games.
    """

    FLOOR = "floor"
    SOLID = "solid"
    BREAKABLE = "breakable"
    SPAWN = "spawn"
    VOID = "void"


def arena_tile_map_from_strings(*rows: str) -> TileMap[ArenaTile]:
    """
    Build a common arena tile map from ASCII rows.
    """

    return tile_map_from_strings(
        *rows,
        legend={
            "#": ArenaTile.SOLID,
            "*": ArenaTile.BREAKABLE,
            ".": ArenaTile.FLOOR,
            "S": ArenaTile.SPAWN,
            " ": ArenaTile.VOID,
        },
        default=ArenaTile.VOID,
    )


def is_walkable_arena_tile(tile: ArenaTile | None) -> bool:
    """
    Return whether an arena tile can be entered by a player/enemy.
    """

    return tile in (ArenaTile.FLOOR, ArenaTile.SPAWN)


@dataclass
class BombState:
    """
    Mutable bomb metadata stored in a bomb field.
    """

    cell: GridCoord
    fuse_seconds: float = 2.0
    blast_range: int = 2
    owner_id: int | None = None
    payload: Any = None


@dataclass
class BombField:
    """
    Dense bomb occupancy keyed by cell.
    """

    bombs: dict[GridCoord, BombState] = field(default_factory=dict)

    def bomb_at(self, cell: GridCoord) -> BombState | None:
        return self.bombs.get(cell)

    def active_bombs(self) -> tuple[BombState, ...]:
        return tuple(self.bombs.values())

    def occupied_cells(self) -> tuple[GridCoord, ...]:
        return tuple(self.bombs.keys())

    def add(self, bomb: BombState) -> BombState:
        self.bombs[bomb.cell] = bomb
        return bomb

    def remove(self, cell: GridCoord) -> BombState | None:
        return self.bombs.pop(cell, None)

    def count_for_owner(self, owner_id: int | None) -> int:
        return sum(
            1
            for bomb in self.bombs.values()
            if bomb.owner_id == owner_id
        )


@dataclass
class ExplosionCellState:
    """
    Mutable active explosion metadata for one cell.
    """

    ttl_seconds: float
    owner_id: int | None = None
    origin: GridCoord | None = None
    payload: Any = None


@dataclass
class ExplosionField:
    """
    Dense active explosion occupancy keyed by cell.
    """

    cells: dict[GridCoord, ExplosionCellState] = field(default_factory=dict)

    def cell_at(self, cell: GridCoord) -> ExplosionCellState | None:
        return self.cells.get(cell)

    def active_cells(self) -> tuple[GridCoord, ...]:
        return tuple(self.cells.keys())

    def set_or_refresh(
        self,
        cell: GridCoord,
        *,
        ttl_seconds: float,
        owner_id: int | None = None,
        origin: GridCoord | None = None,
        payload: Any = None,
    ) -> ExplosionCellState:
        state = self.cells.get(cell)
        if state is None:
            state = ExplosionCellState(
                ttl_seconds=float(ttl_seconds),
                owner_id=owner_id,
                origin=origin,
                payload=payload,
            )
            self.cells[cell] = state
            return state

        state.ttl_seconds = max(float(state.ttl_seconds), float(ttl_seconds))
        state.owner_id = owner_id if owner_id is not None else state.owner_id
        state.origin = origin if origin is not None else state.origin
        state.payload = payload if payload is not None else state.payload
        return state

    def tick(self, dt: float) -> tuple[GridCoord, ...]:
        expired: list[GridCoord] = []
        for cell, state in list(self.cells.items()):
            state.ttl_seconds -= float(dt)
            if state.ttl_seconds <= 0.0:
                expired.append(cell)
                del self.cells[cell]
        return tuple(expired)


def blast_cells(
    tile_map: TileMap[ArenaTile],
    origin: GridCoord,
    *,
    blast_range: int,
) -> tuple[GridCoord, ...]:
    """
    Compute explosion coverage from one bomb origin.
    """

    out: list[GridCoord] = [origin]
    for direction in CardinalDirection:
        current = origin
        for _ in range(max(0, int(blast_range))):
            current = step_in_direction(current, direction)
            tile = tile_map.get(current)
            if tile is None or tile == ArenaTile.VOID:
                break
            if tile == ArenaTile.SOLID:
                break
            out.append(current)
            if tile == ArenaTile.BREAKABLE:
                break
    return tuple(out)


def spawn_explosion_from_bomb(
    explosions: ExplosionField,
    tile_map: TileMap[ArenaTile],
    bomb: BombState,
    *,
    ttl_seconds: float,
) -> tuple[GridCoord, ...]:
    """
    Populate explosion cells from one bomb and return covered cells.
    """

    covered = blast_cells(
        tile_map,
        bomb.cell,
        blast_range=bomb.blast_range,
    )
    for cell in covered:
        explosions.set_or_refresh(
            cell,
            ttl_seconds=ttl_seconds,
            owner_id=bomb.owner_id,
            origin=bomb.cell,
            payload=bomb.payload,
        )
    return covered


@dataclass(frozen=True)
class BombPlacementBinding(Generic[TCtx]):
    """
    Declarative bomb placement rule.
    """

    should_place: Callable[[TCtx], bool]
    placement_cell_getter: Callable[[TCtx], GridCoord]
    bombs_getter: Callable[[TCtx], BombField]
    tile_map_getter: Callable[[TCtx], TileMap[ArenaTile]]
    build_bomb: Callable[[TCtx, GridCoord], BombState]
    owner_id_getter: Callable[[TCtx], int | None] = lambda _ctx: None
    max_active_getter: Callable[[TCtx], int] = lambda _ctx: 1
    on_placed: Callable[[TCtx, BombState], None] | None = None


@dataclass
class BombPlacementSystem(Generic[TCtx]):
    """
    Place bombs onto walkable floor cells when rules allow.
    """

    name: str = "common_bomb_placement"
    phase: int = SystemPhase.SIMULATION
    order: int = 24
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    bindings: tuple[BombPlacementBinding[TCtx], ...] = ()

    def step(self, ctx: TCtx) -> None:
        if not self.enabled_when(ctx):
            return

        for binding in self.bindings:
            if not binding.should_place(ctx):
                continue

            cell = binding.placement_cell_getter(ctx)
            tile_map = binding.tile_map_getter(ctx)
            bombs = binding.bombs_getter(ctx)
            owner_id = binding.owner_id_getter(ctx)

            if not is_walkable_arena_tile(tile_map.get(cell)):
                continue
            if bombs.bomb_at(cell) is not None:
                continue
            if bombs.count_for_owner(owner_id) >= int(binding.max_active_getter(ctx)):
                continue

            bomb = binding.build_bomb(ctx, cell)
            bombs.add(bomb)
            if binding.on_placed is not None:
                binding.on_placed(ctx, bomb)


@dataclass(frozen=True)
class BombFuseBinding(Generic[TCtx]):
    """
    Declarative fuse ticking and detonation rule.
    """

    bombs_getter: Callable[[TCtx], BombField]
    on_detonated: Callable[[TCtx, BombState], None] | None = None


@dataclass
class BombFuseSystem(Generic[TCtx]):
    """
    Tick bomb fuses and emit detonation callbacks when they expire.
    """

    name: str = "common_bomb_fuse"
    phase: int = SystemPhase.SIMULATION
    order: int = 32
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    bindings: tuple[BombFuseBinding[TCtx], ...] = ()

    def step(self, ctx: TCtx) -> None:
        if not self.enabled_when(ctx):
            return

        dt = max(0.0, float(getattr(ctx, "dt", 0.0)))
        if dt <= 0.0:
            return

        for binding in self.bindings:
            bombs = binding.bombs_getter(ctx)
            exploded: list[BombState] = []
            for bomb in list(bombs.active_bombs()):
                bomb.fuse_seconds -= dt
                if bomb.fuse_seconds <= 0.0:
                    removed = bombs.remove(bomb.cell)
                    if removed is not None:
                        exploded.append(removed)

            if binding.on_detonated is None:
                continue
            for bomb in exploded:
                binding.on_detonated(ctx, bomb)


@dataclass(frozen=True)
class ExplosionLifetimeBinding(Generic[TCtx]):
    """
    Declarative active-explosion lifetime rule.
    """

    explosions_getter: Callable[[TCtx], ExplosionField]
    on_expired: Callable[[TCtx, tuple[GridCoord, ...]], None] | None = None


@dataclass
class ExplosionLifetimeSystem(Generic[TCtx]):
    """
    Tick active explosion cells until they expire.
    """

    name: str = "common_explosion_lifetime"
    phase: int = SystemPhase.SIMULATION
    order: int = 38
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    bindings: tuple[ExplosionLifetimeBinding[TCtx], ...] = ()

    def step(self, ctx: TCtx) -> None:
        if not self.enabled_when(ctx):
            return
        dt = max(0.0, float(getattr(ctx, "dt", 0.0)))
        if dt <= 0.0:
            return

        for binding in self.bindings:
            expired = binding.explosions_getter(ctx).tick(dt)
            if expired and binding.on_expired is not None:
                binding.on_expired(ctx, expired)


@dataclass(frozen=True)
class ChainReactionBinding(Generic[TCtx]):
    """
    Declarative bomb chain-reaction rule.
    """

    bombs_getter: Callable[[TCtx], BombField]
    explosions_getter: Callable[[TCtx], ExplosionField]
    on_triggered: Callable[[TCtx, BombState], None] | None = None


@dataclass
class ChainReactionSystem(Generic[TCtx]):
    """
    Trigger bombs early when an active explosion reaches them.
    """

    name: str = "common_chain_reaction"
    phase: int = SystemPhase.SIMULATION
    order: int = 34
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    bindings: tuple[ChainReactionBinding[TCtx], ...] = ()

    def step(self, ctx: TCtx) -> None:
        if not self.enabled_when(ctx):
            return

        for binding in self.bindings:
            bombs = binding.bombs_getter(ctx)
            hot_cells = set(binding.explosions_getter(ctx).active_cells())
            for bomb in bombs.active_bombs():
                if bomb.cell not in hot_cells:
                    continue
                if bomb.fuse_seconds <= 0.0:
                    continue
                bomb.fuse_seconds = 0.0
                if binding.on_triggered is not None:
                    binding.on_triggered(ctx, bomb)


@dataclass(frozen=True)
class DestructibleTileBinding(Generic[TCtx]):
    """
    Declarative breakable-tile destruction rule.
    """

    tile_map_getter: Callable[[TCtx], TileMap[ArenaTile]]
    explosions_getter: Callable[[TCtx], ExplosionField]
    replacement_tile: ArenaTile = ArenaTile.FLOOR
    on_destroyed: Callable[[TCtx, GridCoord], None] | None = None


@dataclass
class DestructibleTileSystem(Generic[TCtx]):
    """
    Destroy breakable tiles touched by active explosion cells.
    """

    name: str = "common_destructible_tiles"
    phase: int = SystemPhase.SIMULATION
    order: int = 36
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    bindings: tuple[DestructibleTileBinding[TCtx], ...] = ()

    def step(self, ctx: TCtx) -> None:
        if not self.enabled_when(ctx):
            return

        for binding in self.bindings:
            tile_map = binding.tile_map_getter(ctx)
            for cell in binding.explosions_getter(ctx).active_cells():
                if tile_map.get(cell) != ArenaTile.BREAKABLE:
                    continue
                tile_map.set(cell, binding.replacement_tile)
                if binding.on_destroyed is not None:
                    binding.on_destroyed(ctx, cell)


@dataclass(frozen=True)
class HazardCollisionBinding(Generic[TCtx]):
    """
    Declarative explosion hazard collision rule.
    """

    hazard_cells_getter: Callable[[TCtx], Iterable[GridCoord]]
    targets_getter: Callable[[TCtx], Iterable[object]]
    target_cell_getter: Callable[[TCtx, object], GridCoord]
    on_hit: Callable[[TCtx, object, GridCoord], None]


@dataclass
class HazardCollisionSystem(Generic[TCtx]):
    """
    Invoke callbacks for targets occupying active hazard cells.
    """

    name: str = "common_hazard_collision"
    phase: int = SystemPhase.SIMULATION
    order: int = 37
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    bindings: tuple[HazardCollisionBinding[TCtx], ...] = ()

    def step(self, ctx: TCtx) -> None:
        if not self.enabled_when(ctx):
            return

        for binding in self.bindings:
            hazards = set(binding.hazard_cells_getter(ctx))
            if not hazards:
                continue
            for target in binding.targets_getter(ctx):
                cell = binding.target_cell_getter(ctx, target)
                if cell not in hazards:
                    continue
                binding.on_hit(ctx, target, cell)


__all__ = [
    "ArenaTile",
    "BombField",
    "BombFuseBinding",
    "BombFuseSystem",
    "BombPlacementBinding",
    "BombPlacementSystem",
    "BombState",
    "ChainReactionBinding",
    "ChainReactionSystem",
    "DestructibleTileBinding",
    "DestructibleTileSystem",
    "ExplosionCellState",
    "ExplosionField",
    "ExplosionLifetimeBinding",
    "ExplosionLifetimeSystem",
    "HazardCollisionBinding",
    "HazardCollisionSystem",
    "arena_tile_map_from_strings",
    "blast_cells",
    "is_walkable_arena_tile",
    "spawn_explosion_from_bomb",
]
