# commands/effect_and_debug_hotkeys

## Goal

Bind function keys and letter keys to toggle visual effects and debug
overlays, and see a live status panel reflect each toggle.

## Why this tutorial exists

Debug tools and visual effects are typically toggled via hotkeys during
development and playtesting.  This example demonstrates:

- using `keys_pressed` to detect single-frame key edges
- toggling boolean flags for bounding boxes, grid overlay, FPS counter
- cycling through background colours
- rendering conditional overlays based on toggle state

## Source map

- Settings profile:
  `examples/settings/commands/effect_and_debug_hotkeys.yml`
- Example builder:
  `examples/catalog/commands/effect_and_debug_hotkeys/main.py`
- Scene:
  `examples/catalog/commands/effect_and_debug_hotkeys/scenes/scene.py`
- Shared runner:
  `examples/_shared/runner.py`

## What to verify

You should see:

1. three coloured rectangles on the canvas
2. a status panel showing each hotkey and its ON/OFF state
3. pressing `F1` draws yellow bounding boxes around the rectangles
4. pressing `F2` shows a grid overlay across the entire viewport
5. pressing `F3` shows an FPS counter in the top-right corner
6. pressing `B` cycles the background colour through five presets

## Controls

| Key | Action |
|-----|--------|
| `F1` | Toggle bounding boxes |
| `F2` | Toggle grid overlay |
| `F3` | Toggle FPS display |
| `B` | Cycle background colour |
| `ESC` | Quit |

## Run

```bash
mini-arcade run --example commands/effect_and_debug_hotkeys
mini-arcade run --example commands/effect_and_debug_hotkeys --pass-through --backend pygame
mini-arcade run --example commands/effect_and_debug_hotkeys --pass-through --backend native
```

## Common mistakes

- Using `keys_held` for toggles — the flag flips every frame the key is
  held.  Use `keys_pressed` for edge detection.
- Hardcoding pixel positions without accounting for virtual resolution
  scaling.
- Drawing debug overlays in the SIMULATION phase instead of RENDERING —
  they get overwritten.

## Related concepts

- [Input Coordinate Mapping Internals](../../concepts/input_coordinate_mapping.md)
- [Scene Internals](../../concepts/scenes_internals.md)

## Next step

This is the last tutorial in Group E.  Continue to the rendering pipeline
tutorials when they become available, or revisit:

- [Scene lifecycle: scene/minimal_scene](../scene/minimal_scene.md)
- [System pipeline: systems/phases_and_order](../systems/phases_and_order.md)
