# systems/input_frame_visualizer

## Goal

Understand the `InputFrame` data model by watching raw keyboard, mouse, and
gamepad state update in real time on a diagnostic dashboard.

## Why this tutorial exists

Every `SimScene.tick()` receives an `InputFrame` snapshot.  Before wiring
action maps or intent systems you need to see what data is available each
frame:

- `keys_held`, `keys_pressed`, `keys_released`
- `mouse_pos`, `mouse_buttons_held`, `mouse_buttons_pressed`
- `axes`, `buttons` (gamepad)

This visualizer renders every field as live text so you can press keys and
see the frame-level effect immediately.

## Source map

- Settings profile:
  `examples/settings/systems/input_frame_visualizer.yml`
- Example builder:
  `examples/catalog/systems/input_frame_visualizer/main.py`
- Scene:
  `examples/catalog/systems/input_frame_visualizer/scenes/scene.py`
- Shared runner:
  `examples/_shared/runner.py`

## What to verify

On screen you should see four labelled columns:

1. **Keys** — held/pressed/released sets update as you type
2. **Mouse** — position tracks the cursor; button sets react to clicks
3. **Axes** — gamepad analog stick values (if a controller is connected)
4. **Buttons** — gamepad digital buttons

Behavior checks:

- pressing a key adds it to `keys_pressed` for exactly one frame, then it
  appears in `keys_held` until released
- `mouse_pos` reflects virtual-coordinate-mapped position
- column labels stay visible even with no input

## Run

```bash
mini-arcade run --example systems/input_frame_visualizer
mini-arcade run --example systems/input_frame_visualizer --pass-through --backend pygame
mini-arcade run --example systems/input_frame_visualizer --pass-through --backend native
```

## Common mistakes

- Confusing `keys_pressed` (edge, one frame) with `keys_held` (level).
- Forgetting that `mouse_pos` is in virtual coordinates, not window pixels.
- Expecting gamepad data without a connected controller.

## Related concepts

- [Input Coordinate Mapping Internals](../../concepts/input_coordinate_mapping.md)

## Next step

- [systems/action_map_variants](action_map_variants.md)
