# window/screen_to_virtual_input

## Goal

Map raw screen-space input into virtual coordinates reliably across viewport modes
and resize changes.

## Why this tutorial exists

Gameplay logic runs in virtual coordinates. Mouse/touch input arrives in screen
coordinates. This mapping must be correct or aiming/clicking drifts.

## Source map

- Settings profile:
  `examples/settings/window/screen_to_virtual_input.yml`
- Example builder:
  `examples/catalog/window/screen_to_virtual_input/main.py`
- Scene:
  `examples/catalog/window/screen_to_virtual_input/scenes/scene.py`
- Input adapter:
  `packages/mini-arcade-core/src/mini_arcade_core/runtime/input/input_adapter.py`
- Window adapter mapping:
  `packages/mini-arcade-core/src/mini_arcade_core/runtime/window/window_adapter.py`
- Viewport mapping math:
  `packages/mini-arcade-core/src/mini_arcade_core/engine/render/viewport.py`

## Runtime flow

1. Backend emits mouse motion events in screen coordinates.
2. `InputAdapter` stores `mouse_pos` in `InputFrame`.
3. Scene calls:
   `services.window.screen_to_virtual(screen_x, screen_y)`.
4. Window adapter applies logical->drawable scaling and viewport transform inverse.
5. Scene uses mapped coordinates in world-space rendering.

## What to verify

1. move mouse and compare `screen mouse` vs `virtual mouse`.
2. switch `FIT`/`FILL` with `1/2`; virtual mapping changes accordingly.
3. in `FIT`, moving inside letterbox bars can yield out-of-bounds virtual values.
4. virtual trail follows mapped world coordinates, not screen coordinates.

## Run

```bash
mini-arcade run --example window/screen_to_virtual_input
```

```bash
mini-arcade run --example window/screen_to_virtual_input --pass-through --backend native
```

## Controls

- Move mouse -> updates mapping
- `1` -> `FIT`
- `2` -> `FILL`
- `C` -> clear virtual trail
- `F1` -> debug overlay
- `ESC` -> quit

## Related concepts

- Input coordinate mapping internals:
  [../../concepts/input_coordinate_mapping.md](../../concepts/input_coordinate_mapping.md)
- Window/viewport internals:
  [../../concepts/window_viewports.md](../../concepts/window_viewports.md)

