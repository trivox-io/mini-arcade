# Maze Gameplay Internals

Mini Arcade now includes a small core toolkit for maze and lane-based arcade
games.

This layer is meant for Pac-Man style prototypes and other games built around:

- tile or maze boards
- four-way lane movement
- buffered turns at junctions
- tunnel wrapping
- collectible fields
- timed gameplay modes

## What lives in core

Core built-ins:

- `CardinalDirection`
- `TileMap`
- `tile_map_from_strings(...)`
- `available_directions(...)`
- `is_junction(...)`
- `GridNavigatorState`
- `GridNavigationBinding`
- `GridNavigationSystem`
- `TunnelWrapBinding`
- `TunnelWrapSystem`
- `CollectibleKind`
- `CollectibleState`
- `CollectibleField`
- `CollectibleCollisionBinding`
- `CollectibleCollisionSystem`
- `TimedMode`
- `ModeTimerState`
- `ModeTimerBinding`
- `ModeTimerSystem`

Source module:

- `packages/mini-arcade-core/src/mini_arcade_core/scenes/systems/builtins/maze.py`

## Tile maps and junction queries

`TileMap` is a dense grid of maze values.

It supports:

- bounds-aware get/set
- iterating all cells
- typed values per cell

`tile_map_from_strings(...)` lets a game author a maze from ASCII rows plus a
legend instead of manually filling the board in code.

`available_directions(...)` and `is_junction(...)` are the reusable query layer
for lane navigation and AI choice logic.

## `GridNavigationSystem`

`GridNavigationSystem` advances one or more agents through a tile map while
supporting buffered direction changes.

Each `GridNavigatorState` stores:

- current cell
- current direction
- pending direction
- how many lane steps moved this frame

The navigation binding can:

- read a desired turn direction from input or AI
- decide whether a tile is enterable
- move multiple cell steps per frame if driven by a cadence/timer layer
- trigger `on_cell_entered(...)` callbacks

This is the core reusable part of Pac-Man style lane movement.

## `TunnelWrapSystem`

`TunnelWrapSystem` wraps navigators across configured grid edges.

Typical use:

- left tunnel exits to right tunnel
- optional vertical wrap for other maze games

This stays separate from `GridNavigationSystem` so games can choose when wrap is
allowed.

## Collectibles

`CollectibleField` stores collectible state by `GridCoord`.

`CollectibleCollisionSystem` removes collectibles when the collector enters the
same cell and emits an optional callback with:

- the collected cell
- the removed `CollectibleState`

That gives game code a clean place to update score, frightened mode, bonus
fruit, and sounds without hardcoding those rules in the field itself.

## Timed modes

`ModeTimerSystem` advances a schedule of `TimedMode` segments.

This is useful for mode-driven arcade gameplay such as:

- scatter
- chase
- frightened
- bonus windows

The system tracks:

- current mode index
- elapsed time in mode
- current mode name

and emits `on_mode_changed(...)` when the schedule advances.

## What is intentionally not in core

Core does not include a full Pac-Man ruleset.

Still game-specific:

- ghost personalities and targeting rules
- house release schedules
- score tables
- fruit rules
- frightened speed tuning
- cutscenes
- exact maze layouts and content

Those should live in game code on top of the reusable maze primitives above.
