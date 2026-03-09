# window/resize_reflow

## Goal

Learn how to make layout react to window size changes without breaking world-space
simulation.

## Why this tutorial exists

Games need both:

- stable world-space rendering in virtual coordinates
- responsive UI anchored to screen edges

This tutorial demonstrates both in one scene.

## Source map

- Settings profile:
  `examples/settings/window/resize_reflow.yml`
- Example builder:
  `examples/catalog/window/resize_reflow/main.py`
- Scene:
  `examples/catalog/window/resize_reflow/scenes/scene.py`
- Render passes:
  `packages/mini-arcade-core/src/mini_arcade_core/engine/render/passes/world.py`
  `packages/mini-arcade-core/src/mini_arcade_core/engine/render/passes/ui.py`

## Runtime flow

1. Window resize events update viewport state in window service.
2. Scene reads fresh `vp.window_w/h` each tick.
3. World draw op stays in virtual space (`world` pass).
4. UI draw op recomputes panel/footer layout in screen space (`ui` pass).

## What to verify

Resize the window continuously.

1. world marker movement remains stable in virtual space.
2. top-right panel reflows based on current window size.
3. bottom footer stretches with window width.
4. `resize count` increases when dimensions change.

## Run

```bash
mini-arcade run --example window/resize_reflow
```

```bash
mini-arcade run --example window/resize_reflow --pass-through --backend native
```

## Controls

- Resize the window
- `F1` -> debug overlay
- `ESC` -> quit

## Related concepts

- Window and viewport internals:
  [../../concepts/window_viewports.md](../../concepts/window_viewports.md)
- Render pass separation (`world` vs `ui`):
  [../../concepts/scenes_internals.md](../../concepts/scenes_internals.md)

## Next step

- Map input from screen-space to virtual-space:
  [screen_to_virtual_input.md](screen_to_virtual_input.md)
