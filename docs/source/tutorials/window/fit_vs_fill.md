# window/fit_vs_fill

## Goal

Compare `FIT` vs `FILL` viewport modes and understand letterbox vs crop tradeoffs.

## Why this tutorial exists

This is a core decision for any game:

- preserve full virtual frame (`FIT`)
- or fill full window without bars (`FILL`)

## Source map

- Settings profile:
  `examples/settings/window/fit_vs_fill.yml`
- Example builder:
  `examples/catalog/window/fit_vs_fill/main.py`
- Scene:
  `examples/catalog/window/fit_vs_fill/scenes/scene.py`
- Viewport mode enum:
  `packages/mini-arcade-core/src/mini_arcade_core/engine/render/viewport.py`

## Runtime flow

`set_viewport_mode(...)` updates `Viewport.mode`, then recomputes:

- `scale`
- `viewport_w` / `viewport_h`
- `offset_x` / `offset_y`

The tutorial visualizes:

- full virtual border
- currently visible virtual bounds

So cropping in `FILL` is explicit.

## What to verify

1. `1` (`FIT`) shows all virtual edges, with bars if needed.
2. `2` (`FILL`) removes bars but crops top/bottom or left/right.
3. `visible virtual bounds` shrink in `FILL`.
4. `offset` can become negative in `FILL` mode.

## Run

```bash
mini-arcade run --example window/fit_vs_fill
```

```bash
mini-arcade run --example window/fit_vs_fill --pass-through --backend native
```

## Controls

- `1` -> `FIT`
- `2` -> `FILL`
- `F1` -> debug overlay
- `ESC` -> quit

## Related concepts

- Window and viewport internals:
  [../../concepts/window_viewports.md](../../concepts/window_viewports.md)
- Input mapping implications:
  [../../concepts/input_coordinate_mapping.md](../../concepts/input_coordinate_mapping.md)

## Next step

- Build resize-responsive layout:
  [resize_reflow.md](resize_reflow.md)
