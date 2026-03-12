"""
Reusable falling-block gameplay helpers for stacking puzzle games.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable, Generic, Iterable, TypeVar

from mini_arcade_core.scenes.systems.builtins.grid import GridCoord
from mini_arcade_core.scenes.systems.phases import SystemPhase

# pylint: disable=invalid-name
TCtx = TypeVar("TCtx")
TCell = TypeVar("TCell")
TItem = TypeVar("TItem")
# pylint: enable=invalid-name


def _default_enabled_when(_ctx: object) -> bool:
    return True


def block_cells_from_strings(
    *rows: str,
    filled_chars: str = "#XO@[]",
) -> tuple[GridCoord, ...]:
    """
    Parse one rotation from ASCII rows into local grid cells.
    """

    filled = set(str(filled_chars))
    out: list[GridCoord] = []
    for row_idx, row in enumerate(rows):
        for col_idx, char in enumerate(str(row)):
            if char in filled:
                out.append(GridCoord(col=col_idx, row=row_idx))
    return tuple(out)


@dataclass
class BlockBoard(Generic[TCell]):
    """
    Dense visible board state for stacking puzzle games.
    """

    cols: int
    rows: int
    empty: TCell | None = None
    _cells: list[list[TCell | None]] = field(
        default_factory=list,
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        self._cells = [
            [self.empty for _ in range(int(self.cols))]
            for _ in range(int(self.rows))
        ]

    def in_bounds(self, coord: GridCoord) -> bool:
        """
        Return whether a cell lies inside the visible board.
        """

        return (
            0 <= int(coord.col) < int(self.cols)
            and 0 <= int(coord.row) < int(self.rows)
        )

    def get(self, coord: GridCoord) -> TCell | None:
        """
        Return the stored value for a visible cell.
        """

        if not self.in_bounds(coord):
            return None
        return self._cells[int(coord.row)][int(coord.col)]

    def set(self, coord: GridCoord, value: TCell | None) -> None:
        """
        Write a value into a visible cell.
        """

        if not self.in_bounds(coord):
            raise IndexError(f"Cell out of bounds: {coord!r}")
        self._cells[int(coord.row)][int(coord.col)] = value

    def clear(self, coord: GridCoord) -> None:
        """
        Reset one visible cell to the configured empty value.
        """

        self.set(coord, self.empty)

    def row_values(self, row: int) -> tuple[TCell | None, ...]:
        """
        Return one row as an immutable tuple.
        """

        return tuple(self._cells[int(row)])

    def row_is_filled(self, row: int) -> bool:
        """
        Return whether a row contains no empty cells.
        """

        return all(cell is not None for cell in self._cells[int(row)])

    def filled_rows(self) -> tuple[int, ...]:
        """
        Return the indexes of completely filled rows.
        """

        return tuple(
            row for row in range(int(self.rows)) if self.row_is_filled(row)
        )

    def occupied_cells(self) -> tuple[GridCoord, ...]:
        """
        Return the coordinates of all non-empty cells.
        """

        out: list[GridCoord] = []
        for row in range(int(self.rows)):
            for col in range(int(self.cols)):
                if self._cells[row][col] is not None:
                    out.append(GridCoord(col=col, row=row))
        return tuple(out)

    def occupied_entries(self) -> tuple[tuple[GridCoord, TCell], ...]:
        """
        Return coordinates paired with stored cell values.
        """

        out: list[tuple[GridCoord, TCell]] = []
        for row in range(int(self.rows)):
            for col in range(int(self.cols)):
                value = self._cells[row][col]
                if value is None:
                    continue
                out.append((GridCoord(col=col, row=row), value))
        return tuple(out)

    def can_place(
        self,
        cells: Iterable[GridCoord],
        *,
        allow_rows_above_board: bool = False,
    ) -> bool:
        """
        Return whether the given cells can be occupied without collisions.
        """

        for coord in cells:
            if int(coord.col) < 0 or int(coord.col) >= int(self.cols):
                return False
            if int(coord.row) >= int(self.rows):
                return False
            if int(coord.row) < 0:
                if allow_rows_above_board:
                    continue
                return False
            if self.get(coord) is not None:
                return False
        return True

    def stamp(
        self,
        cells: Iterable[GridCoord],
        *,
        value: TCell,
        ignore_rows_above_board: bool = True,
    ) -> tuple[GridCoord, ...]:
        """
        Write one value into multiple cells and return written coordinates.
        """

        written: list[GridCoord] = []
        for coord in cells:
            if int(coord.row) < 0 and ignore_rows_above_board:
                continue
            self.set(coord, value)
            written.append(coord)
        return tuple(written)

    def collapse_rows(self, rows: Iterable[int]) -> tuple[int, ...]:
        """
        Remove filled rows and shift higher rows downward.
        """

        unique_rows = tuple(sorted({int(row) for row in rows}))
        if not unique_rows:
            return ()

        removed = set(unique_rows)
        survivors = [
            list(self._cells[row])
            for row in range(int(self.rows))
            if row not in removed
        ]
        while len(survivors) < int(self.rows):
            survivors.insert(0, [self.empty for _ in range(int(self.cols))])
        self._cells = survivors
        return unique_rows


@dataclass(frozen=True)
class FallingBlockPieceSpec:
    """
    One falling-piece definition with precomputed rotation states.
    """

    name: str
    rotations: tuple[tuple[GridCoord, ...], ...]

    def __post_init__(self) -> None:
        if not self.rotations:
            raise ValueError("rotations must not be empty")

    def cells(self, rotation: int = 0) -> tuple[GridCoord, ...]:
        """
        Return the local cells for the normalized rotation index.
        """

        index = int(rotation) % len(self.rotations)
        return self.rotations[index]


@dataclass(frozen=True)
class FallingBlockPiece:
    """
    Active falling piece instance positioned on a board grid.
    """

    spec_name: str
    origin: GridCoord
    rotation: int = 0

    def translated(
        self,
        *,
        dcol: int = 0,
        drow: int = 0,
    ) -> "FallingBlockPiece":
        """
        Return a translated copy of the active piece.
        """

        return FallingBlockPiece(
            spec_name=self.spec_name,
            origin=self.origin.translated(dcol=dcol, drow=drow),
            rotation=int(self.rotation),
        )

    def rotated(self, delta: int = 1) -> "FallingBlockPiece":
        """
        Return a copy rotated by a relative delta.
        """

        return FallingBlockPiece(
            spec_name=self.spec_name,
            origin=self.origin,
            rotation=int(self.rotation) + int(delta),
        )

    def cells(self, spec: FallingBlockPieceSpec) -> tuple[GridCoord, ...]:
        """
        Return the occupied board cells for this active piece.
        """

        return tuple(
            self.origin.translated(dcol=cell.col, drow=cell.row)
            for cell in spec.cells(self.rotation)
        )


def piece_fits(
    board: BlockBoard[TCell],
    piece: FallingBlockPiece,
    spec: FallingBlockPieceSpec,
    *,
    allow_rows_above_board: bool = False,
) -> bool:
    """
    Return whether an active piece fits on a board without collisions.
    """

    return board.can_place(
        piece.cells(spec),
        allow_rows_above_board=allow_rows_above_board,
    )


@dataclass
class BagRandomizer(Generic[TItem]):
    """
    Deterministic bag-based sequence generator.
    """

    items: tuple[TItem, ...]
    seed: int = 1
    _bag: list[TItem] = field(default_factory=list, init=False, repr=False)
    _rng: random.Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.items:
            raise ValueError("items must not be empty")
        self._rng = random.Random(int(self.seed))

    def refill(self) -> tuple[TItem, ...]:
        """
        Refill and shuffle the current bag.
        """

        self._bag = list(self.items)
        self._rng.shuffle(self._bag)
        return tuple(self._bag)

    def next(self) -> TItem:
        """
        Draw the next item, refilling the bag as needed.
        """

        if not self._bag:
            self.refill()
        return self._bag.pop(0)

    def peek(self) -> tuple[TItem, ...]:
        """
        Return the remaining contents of the current bag.
        """

        return tuple(self._bag)


@dataclass(frozen=True)
class BoardRowClearBinding(Generic[TCtx]):
    """
    Declarative row-clear rule for one falling-block board.
    """

    board_getter: Callable[[TCtx], BlockBoard[object]]
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    on_cleared: Callable[[TCtx, tuple[int, ...]], None] | None = None


@dataclass
class BoardRowClearSystem(Generic[TCtx]):
    """
    Clear fully occupied rows and collapse the board downward.
    """

    name: str = "common_board_row_clear"
    phase: int = SystemPhase.SIMULATION
    order: int = 70
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    bindings: tuple[BoardRowClearBinding[TCtx], ...] = ()

    def step(self, ctx: TCtx) -> None:
        if not self.enabled_when(ctx):
            return

        for binding in self.bindings:
            if not binding.enabled_when(ctx):
                continue
            board = binding.board_getter(ctx)
            cleared = board.collapse_rows(board.filled_rows())
            if not cleared:
                continue
            if binding.on_cleared is not None:
                binding.on_cleared(ctx, cleared)


__all__ = [
    "BagRandomizer",
    "BlockBoard",
    "BoardRowClearBinding",
    "BoardRowClearSystem",
    "FallingBlockPiece",
    "FallingBlockPieceSpec",
    "block_cells_from_strings",
    "piece_fits",
]
