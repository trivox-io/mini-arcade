# Bomberman Gameplay Internals

Mini Arcade now includes a small core toolkit for bomb-and-arena arcade games.

This layer is meant for Bomberman-style prototypes and other games built
around:

- arena tile maps
- timed bombs
- directional blast propagation
- chain reactions
- destructible blocks
- short-lived hazard fields

## What lives in core

Core built-ins:

- `ArenaTile`
- `arena_tile_map_from_strings(...)`
- `BombState`
- `BombField`
- `BombPlacementBinding`
- `BombPlacementSystem`
- `BombFuseBinding`
- `BombFuseSystem`
- `ExplosionCellState`
- `ExplosionField`
- `ExplosionLifetimeBinding`
- `ExplosionLifetimeSystem`
- `ChainReactionBinding`
- `ChainReactionSystem`
- `DestructibleTileBinding`
- `DestructibleTileSystem`
- `HazardCollisionBinding`
- `HazardCollisionSystem`
- `blast_cells(...)`
- `spawn_explosion_from_bomb(...)`

Source module:

- `packages/mini-arcade-core/src/mini_arcade_core/scenes/systems/builtins/bomberman.py`

## Arena tiles

`ArenaTile` standardizes the common tile categories used by bomb-based grid
games:

- `FLOOR`
- `SOLID`
- `BREAKABLE`
- `SPAWN`
- `VOID`

`arena_tile_map_from_strings(...)` lets a game define those tiles from ASCII
rows instead of building the map cell by cell.

## Bomb placement and fuse timing

`BombPlacementSystem` is the reusable rule for:

- checking whether placement is requested
- checking whether the target cell is walkable
- enforcing one bomb per cell
- enforcing per-owner active bomb limits
- inserting the new `BombState`

`BombFuseSystem` handles the countdown side:

- tick fuse timers
- remove expired bombs from `BombField`
- invoke game-specific detonation callbacks

That keeps placement capacity and fuse timing reusable while game code stays in
control of scoring, audio, and visuals.

## Blast propagation and chain reactions

`blast_cells(...)` computes directional explosion coverage from one origin.

The propagation rules are reusable and match the common pattern:

- include the origin cell
- stop at solid walls
- include a breakable tile, then stop
- stop at out-of-bounds or void cells

`spawn_explosion_from_bomb(...)` is a convenience helper that translates a
detonated `BombState` into live cells in an `ExplosionField`.

`ChainReactionSystem` then handles the next rule layer: bombs touched by active
explosion cells can be forced to detonate early.

## Destruction and hazards

`DestructibleTileSystem` turns breakable tiles into a replacement tile when
active explosion cells overlap them.

`HazardCollisionSystem` is the generic damage/hit layer for any target type.
Games supply:

- which cells are hazardous
- which targets to test
- how to read a target cell
- what to do on a hit

This keeps player death, enemy damage, item ignition, and similar effects out
of the tile/explosion data structures themselves.

## Explosion lifetime

`ExplosionField` stores short-lived active flame cells.

`ExplosionLifetimeSystem` ticks those cells down and removes them when their
TTL expires. This is the reusable cleanup layer for Bomberman-style hazards.

## What is intentionally not in core

Core does not include a full Bomberman ruleset.

Still game-specific:

- player movement rules and collision feel
- enemy AI and stage progression
- score and versus mode rules
- item catalogs and pickup effects
- bomb kick, throw, or remote-detonation behaviors
- art, audio, HUD, and exact map content

Those should live in game code on top of the reusable arena/bomb primitives
above.
