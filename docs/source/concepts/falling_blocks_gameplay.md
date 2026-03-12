# Falling Blocks Internals

Mini Arcade now includes a small core toolkit for stacking puzzle and
falling-block games.

This layer is meant for Tetris-like prototypes and other games built around:

- a dense board
- active falling pieces
- row clearing
- deterministic piece sequencing

## What lives in core

Core built-ins:

- `BlockBoard`
- `FallingBlockPieceSpec`
- `FallingBlockPiece`
- `block_cells_from_strings(...)`
- `piece_fits(...)`
- `BagRandomizer`
- `BoardRowClearBinding`
- `BoardRowClearSystem`

Source module:

- `packages/mini-arcade-core/src/mini_arcade_core/scenes/systems/builtins/falling_blocks.py`

## `BlockBoard`

`BlockBoard` is a dense visible board model with:

- fixed `cols` and `rows`
- cell get/set/clear
- filled-row queries
- occupied-cell iteration
- collision checks for candidate piece cells
- row collapse after clears

This is intentionally board-state only. It does not own scoring, piece queues,
hold rules, wall kicks, or rendering.

## Piece specs and active pieces

`FallingBlockPieceSpec` stores the precomputed rotation states for one piece.

`FallingBlockPiece` stores:

- piece/spec id
- board origin
- current rotation index

Together they provide:

- translated piece copies
- rotated piece copies
- occupied board cells for the active piece

`block_cells_from_strings(...)` is a small authoring helper for defining
rotations from ASCII rows instead of manually writing `GridCoord(...)` tuples.

## `piece_fits(...)`

`piece_fits(...)` checks whether a piece can occupy a board without:

- crossing horizontal bounds
- falling below the board
- colliding with settled cells

It also supports `allow_rows_above_board=True`, which is useful for spawn logic
where a piece can begin partially above the visible board.

## `BagRandomizer`

`BagRandomizer` is a deterministic bag-based sequence helper.

It is useful for:

- 7-bag piece sequencing
- deterministic tests
- predictable replays when the game stores the seed

This lives in core because it is a reusable gameplay primitive, not a Tetris UI
feature.

## `BoardRowClearSystem`

`BoardRowClearSystem` clears fully occupied rows and collapses the board
downward.

A binding:

- resolves the board from scene/world state
- optionally gates whether row clearing is active
- can react to cleared rows through `on_cleared(...)`

That callback is where a concrete game would update:

- score
- combo state
- sound triggers
- animation requests

## What is intentionally not in core

Core does not include a full Tetris ruleset.

Still game-specific:

- scoring tables
- level/speed progression
- hold piece rules
- next queue presentation
- ghost piece visuals
- DAS/ARR tuning
- lock delay
- wall-kick tables and rotation systems

Those should sit in game code on top of the generic falling-block primitives.
