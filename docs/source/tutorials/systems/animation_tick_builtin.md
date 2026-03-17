# systems/animation_tick_builtin

## Goal

See how `AnimationTickSystem` advances `Anim2D` frame data automatically
each tick, and visualize the frame strips it produces.

## Why this tutorial exists

Sprite animation requires stepping through frames at a configurable rate.
The built-in `AnimationTickSystem`:

- reads `Anim2D.frame_duration` and `Anim2D.frame_count`
- advances `Anim2D.current_frame` based on elapsed `dt`
- supports looping and one-shot modes

This example creates entities with different animation configs and renders
coloured frame strips so you can see the frame index change over time.

## Source map

- Settings profile:
  `examples/settings/systems/animation_tick_builtin.yml`
- Example builder:
  `examples/catalog/systems/animation_tick_builtin/main.py`
- Scene:
  `examples/catalog/systems/animation_tick_builtin/scenes/scene.py`
- Shared runner:
  `examples/_shared/runner.py`

## What to verify

You should see:

1. multiple horizontal frame strips, one per entity
2. the current frame highlighted in a brighter colour
3. faster-configured entities cycle through frames more quickly
4. one-shot entities stop at the last frame instead of looping

Behavior checks:

- frame index resets to 0 at the end of a looping animation
- one-shot animations freeze on the last frame

## Run

```bash
mini-arcade run --example systems/animation_tick_builtin
mini-arcade run --example systems/animation_tick_builtin --pass-through --backend pygame
mini-arcade run --example systems/animation_tick_builtin --pass-through --backend native
```

## Common mistakes

- Setting `frame_duration` to 0 — causes division by zero or instant
  cycling.
- Forgetting to set `frame_count` — the system cannot advance without
  knowing how many frames exist.
- Expecting the system to handle sprite-sheet UV mapping — it only manages
  the frame index.

## Related concepts

- [Sprites and Animations Internals](../../concepts/sprites_animations.md)
- [Entities Internals](../../concepts/entities.md)

## Next step

- [systems/cull_viewport_builtin](cull_viewport_builtin.md)
