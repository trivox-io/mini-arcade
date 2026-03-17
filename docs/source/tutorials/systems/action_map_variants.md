# systems/action_map_variants

## Goal

Learn how to declare an `ActionMap` that translates raw input into named
actions, and see how digital (on/off) and axis (continuous) bindings work
together.

## Why this tutorial exists

Raw `InputFrame` data is low-level.  Most gameplay code should read logical
actions ("move_left", "shoot") instead of raw keys.  This tutorial shows:

- building an `ActionMap` with digital key bindings
- adding axis bindings for analog input
- querying action state each frame
- rendering a moving rectangle driven by mapped actions

## Source map

- Settings profile:
  `examples/settings/systems/action_map_variants.yml`
- Example builder:
  `examples/catalog/systems/action_map_variants/main.py`
- Scene:
  `examples/catalog/systems/action_map_variants/scenes/scene.py`
- Shared runner:
  `examples/_shared/runner.py`

## What to verify

You should see:

1. a cyan rectangle that moves with arrow keys and WASD
2. a status panel listing every mapped action and its current value
3. axis values changing smoothly when a gamepad stick is used

Behavior checks:

- holding Left Arrow and A at the same time does not double the speed
  (digital bindings clamp to 0/1)
- releasing all keys returns the action values to zero
- the panel updates every frame

## Run

```bash
mini-arcade run --example systems/action_map_variants
mini-arcade run --example systems/action_map_variants --pass-through --backend pygame
mini-arcade run --example systems/action_map_variants --pass-through --backend native
```

## Common mistakes

- Defining the same action name twice with conflicting binding types.
- Forgetting that digital bindings produce `0.0` / `1.0`, not booleans.
- Not scaling movement by `dt`, causing frame-rate-dependent speed.

## Related concepts

- [Input Coordinate Mapping Internals](../../concepts/input_coordinate_mapping.md)

## Next step

- [systems/phases_and_order](phases_and_order.md)
