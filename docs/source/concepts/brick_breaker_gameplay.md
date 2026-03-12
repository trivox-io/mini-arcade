# Brick Breaker Internals

Mini Arcade now includes a small core toolkit for Breakout / Arkanoid style
games.

This layer is meant for games built around:

- a bouncing ball
- paddle-shaped bounce response
- brick layouts with hit points
- brick hit / clear gameplay loops

## What lives in core

Core built-ins:

- `BounceHit`
- `resolve_rect_bounce(...)`
- `apply_bounce_hit(...)`
- `ViewportBounceBinding`
- `ViewportBounceSystem`
- `BounceCollisionBinding`
- `BounceCollisionSystem`
- `PaddleBouncePolicy`
- `BrickState`
- `BrickField`
- `BrickFieldCollisionBinding`
- `BrickFieldCollisionSystem`

Source module:

- `packages/mini-arcade-core/src/mini_arcade_core/scenes/systems/builtins/brick_breaker.py`

## Viewport bounce

`ViewportBounceSystem` handles the common ball-vs-wall case for selected
viewport sides.

Typical use:

- bounce from left, right, and top
- let bottom pass through for life-loss logic

The system repositions the ball inside the viewport and reflects the relevant
velocity component.

## Rect bounce collisions

`BounceCollisionSystem` handles one moving rect against one or more target
rects.

`resolve_rect_bounce(...)` computes:

- collision axis
- bounce normal
- penetration depth

`apply_bounce_hit(...)` then resolves the overlap and reflects velocity on the
chosen axis.

This is intended for:

- ball vs paddle
- ball vs moving shield
- ball vs bumpers

## `PaddleBouncePolicy`

`PaddleBouncePolicy` reshapes the outgoing ball trajectory based on where it
hits the paddle.

It supports:

- horizontal offset shaping
- min/max speed
- speed gain after impact
- paddle velocity influence

This is the core reusable part of classic paddle-ball gameplay. Exact score,
combo, and power-up rules still belong in the game.

## `BrickField`

`BrickField` is a simple dense brick layout keyed by `GridCoord`.

Each cell stores a `BrickState`:

- `hit_points`
- optional `payload`

The field exposes:

- alive brick queries
- brick rect lookup through `GridLayout`
- damage application and brick removal

This keeps brick state separate from scene-specific UI or score logic.

## `BrickFieldCollisionSystem`

`BrickFieldCollisionSystem` reflects a ball from the first hit brick in a field
and applies damage to that brick cell.

The binding callback receives:

- the hit cell
- the remaining brick state, if any
- the resolved bounce hit

That gives game code a clean place to:

- award score
- spawn drops
- play sounds
- track combo/chain rules

## What is intentionally not in core

Core does not include a full Arkanoid ruleset.

Still game-specific:

- score tables
- lives / restart rules
- level progression
- power-up catalogs
- laser paddles
- sticky/catch paddles
- multiball rules
- enemy waves or bosses

Those should be implemented in game code on top of the reusable helpers above.
