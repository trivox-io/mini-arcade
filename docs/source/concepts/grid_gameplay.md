# Grid Gameplay Internals

Mini Arcade now includes a small core toolkit for discrete, cell-based games.

This layer is meant for games like Snake, Pac-Man-style prototypes, board games,
or any gameplay loop that advances in fixed cell steps instead of continuous
float motion.

## What lives in core

Core built-ins:

- `CadenceState`
- `CadenceBinding`
- `CadenceSystem`
- `GridCoord`
- `GridBounds`
- `GridLayout`
- `occupied_grid_cells(...)`
- `free_grid_cells(...)`
- `GridCellSpawnBinding`
- `GridCellSpawnSystem`

Source module:

- `packages/mini-arcade-core/src/mini_arcade_core/scenes/systems/builtins/grid.py`

## `CadenceSystem`

`CadenceSystem` is the fixed-step helper for gameplay that should advance on a
logical interval rather than every render frame.

Typical use:

- snake movement every `0.12s`
- board/turn simulation every `0.20s`
- timed hazard pulses every `0.50s`

Each binding owns a mutable `CadenceState` in the world:

- `accumulator`: leftover frame time
- `tick_count`: total fixed ticks emitted
- `steps_this_frame`: how many fixed ticks ran this render frame

That lets a scene keep rendering at 60 FPS while the gameplay advances on a
slower logical cadence.

## Grid coordinates and layout

`GridCoord` is an integer `(col, row)` pair.

`GridBounds` defines the playable cell rectangle:

- containment checks
- iteration over every cell

`GridLayout` converts logical cells into world-space positions:

- `cell_origin(...)`
- `cell_center(...)`
- `cell_rect(...)`

This keeps rendering and gameplay separate:

- gameplay works in cells
- rendering works in pixels / virtual coordinates

## Occupancy helpers

`occupied_grid_cells(...)` collects blocked cells from arbitrary scene values.

`free_grid_cells(...)` returns all non-occupied cells inside a `GridBounds`.

These helpers are intentionally simple and data-oriented. They do not assume an
entity model or a specific game rule.

## `GridCellSpawnSystem`

`GridCellSpawnSystem` is the grid equivalent of the generic spawn helpers.

A binding:

- decides whether spawning should happen now
- provides current bounds
- provides occupied cells
- chooses one free cell
- builds one or more entities for that cell

This is useful for:

- food pickup spawning
- bonus item placement
- trap placement
- deterministic board setup

By default, the system uses `choose_first_grid_cell(...)`, but callers can pass
their own chooser for random or weighted placement.

## What is intentionally not in core

Core does not include Snake-specific rules such as:

- buffered direction changes
- instant reverse-turn rejection
- score/length rules
- tail-follow rules
- self-collision semantics

Those belong in game systems built on top of the generic grid primitives above.
