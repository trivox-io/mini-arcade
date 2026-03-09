# window/virtual_resolution_basics

## Goal

Understand what virtual resolution controls and how it differs from window size.

## Why this tutorial exists

Most gameplay code should think in virtual coordinates, not physical window
pixels. This tutorial makes that separation visible.

## Source map

- Settings profile:
  `examples/settings/window/virtual_resolution_basics.yml`
- Example builder:
  `examples/catalog/window/virtual_resolution_basics/main.py`
- Scene:
  `examples/catalog/window/virtual_resolution_basics/scenes/scene.py`
- Window adapter:
  `packages/mini-arcade-core/src/mini_arcade_core/runtime/window/window_adapter.py`
- Viewport math:
  `packages/mini-arcade-core/src/mini_arcade_core/engine/render/viewport.py`

## Runtime flow

1. Engine starts with `engine_config.virtual_resolution`.
2. Scene can update it at runtime with:
   `services.window.set_virtual_resolution(width, height)`.
3. Viewport state recomputes:
   scale, viewport rectangle, and offsets.
4. World rendering keeps using virtual-space coordinates.

## What to verify

Use keys `1/2/3` to switch virtual resolution.

You should see:

1. `runtime virtual` changes immediately.
2. corner markers remain at virtual edges.
3. world layout meaning is stable, while scale/letterbox changes.
4. `window` size remains independent from virtual size.

## Run

Default:

```bash
mini-arcade run --example window/virtual_resolution_basics
```

Force backend:

```bash
mini-arcade run --example window/virtual_resolution_basics --pass-through --backend pygame
mini-arcade run --example window/virtual_resolution_basics --pass-through --backend native
```

Override startup virtual resolution:

```bash
mini-arcade run --example window/virtual_resolution_basics --pass-through --virtual-width 960 --virtual-height 540
```

## Controls

- `1` -> virtual `640x360`
- `2` -> virtual `800x600`
- `3` -> virtual `960x540`
- `F1` -> debug overlay
- `ESC` -> quit

## Related concepts

- Window and viewport internals:
  [../../concepts/window_viewports.md](../../concepts/window_viewports.md)
- Scene internals:
  [../../concepts/scenes_internals.md](../../concepts/scenes_internals.md)

## Next step

- Compare viewport policies:
  [fit_vs_fill.md](fit_vs_fill.md)
