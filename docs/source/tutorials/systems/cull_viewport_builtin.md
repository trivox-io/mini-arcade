# systems/cull_viewport_builtin

## Goal

See how `CullOutOfViewportSystem` automatically removes entities that leave
the visible area, and watch a spawn counter track creation vs culling.

## Why this tutorial exists

In many games, projectiles, particles, or enemies that leave the screen
should be cleaned up.  The built-in `CullOutOfViewportSystem`:

- checks each entity's transform against the viewport bounds
- removes entities that are fully outside the viewport
- fires callbacks or increments counters for monitoring

This example continuously spawns entities that move in random directions and
displays real-time spawn and cull counters.

## Source map

- Settings profile:
  `examples/settings/systems/cull_viewport_builtin.yml`
- Example builder:
  `examples/catalog/systems/cull_viewport_builtin/main.py`
- Scene:
  `examples/catalog/systems/cull_viewport_builtin/scenes/scene.py`
- Shared runner:
  `examples/_shared/runner.py`

## What to verify

You should see:

1. coloured rectangles spawning from the centre and drifting outward
2. entities disappearing as they leave the viewport edge
3. a panel showing spawned / culled / active counts
4. active count stays bounded (culling keeps up with spawning)

Behavior checks:

- resizing the window changes the effective cull boundary
- entities touching the edge are not culled — only fully outside ones
- the active count stabilizes after a few seconds

## Run

```bash
mini-arcade run --example systems/cull_viewport_builtin
mini-arcade run --example systems/cull_viewport_builtin --pass-through --backend pygame
mini-arcade run --example systems/cull_viewport_builtin --pass-through --backend native
```

## Common mistakes

- Culling entities that should wrap around (use viewport wrapping instead).
- Setting the cull margin to 0 — entities flicker at the exact edge.
- Forgetting that the system uses virtual coordinates, not pixel
  coordinates.

## Related concepts

- [Window and Viewport Internals](../../concepts/window_viewports.md)
- [Entities Internals](../../concepts/entities.md)

## Next step

- [commands/custom_scene_commands](../commands/custom_scene_commands.md)
