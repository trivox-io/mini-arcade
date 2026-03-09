# Window and Viewport Internals

## Purpose

Explain how virtual resolution, window size, viewport mode, and resize updates
interact in runtime rendering.

## Core files

- `packages/mini-arcade-core/src/mini_arcade_core/runtime/window/window_adapter.py`
- `packages/mini-arcade-core/src/mini_arcade_core/engine/render/viewport.py`
- `packages/mini-arcade-core/src/mini_arcade_core/engine/render/passes/world.py`
- `packages/mini-arcade-core/src/mini_arcade_core/engine/render/passes/ui.py`

## Virtual vs window resolution

- virtual resolution:
  simulation/render space (`virtual_w`, `virtual_h`)
- window resolution:
  presentation size (`window_w`, `window_h`)

`set_virtual_resolution(w, h)` updates virtual canvas and recomputes viewport
scale/offset for current window size.

## Viewport modes

`ViewportMode.FIT`:

- `scale = min(window_w/virtual_w, window_h/virtual_h)`
- full virtual frame visible
- letterbox/pillarbox bars may appear

`ViewportMode.FILL`:

- `scale = max(window_w/virtual_w, window_h/virtual_h)`
- fills window
- virtual frame is cropped on one axis

## Viewport state fields

`ViewportState` includes:

- virtual size
- window size
- mode
- scale
- viewport rectangle (`viewport_w`, `viewport_h`, `offset_x`, `offset_y`)

Offsets can be negative in `FILL` mode.

## Resize propagation

1. backend emits `WINDOWRESIZED`
2. loop hook calls `window.on_window_resized(w, h)`
3. adapter updates logical/drawable sizes
4. viewport recomputes scale/offset
5. render passes consume updated viewport on next frame

## World pass vs UI pass

World pass:

- applies viewport transform and virtual clipping
- use for gameplay/world entities

UI pass:

- clears viewport transform and clip
- use for screen-space overlays/layout

This separation is the basis for responsive reflow on resize.

## Tutorial references

- `docs/source/tutorials/window/virtual_resolution_basics.md`
- `docs/source/tutorials/window/fit_vs_fill.md`
- `docs/source/tutorials/window/resize_reflow.md`

