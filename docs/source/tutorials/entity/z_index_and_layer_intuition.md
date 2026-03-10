# entity/z_index_and_layer_intuition

## Goal

Understand the difference between `z_index` and `render_layer`.

## Why this tutorial exists

These two fields solve different ordering problems:

- `z_index`:
  order inside the same render layer
- `render_layer`:
  move the entity to another render pass such as `ui`

If you mix them up, world entities may draw in the wrong order or UI elements
may accidentally live inside the world pass.

## Source map

- Settings profile:
  `examples/settings/entity/z_index_and_layer_intuition.yml`
- Example builder:
  `examples/catalog/entity/z_index_and_layer_intuition/main.py`
- Scene:
  `examples/catalog/entity/z_index_and_layer_intuition/scenes/scene.py`
- Built-in queued renderer:
  `packages/mini-arcade-core/src/mini_arcade_core/scenes/systems/builtins/__init__.py`

## What to verify

You should see:

1. three overlapping world-layer cards
2. the top card covering the lower cards because of higher `z_index`
3. a gold badge that stays above the stack because it uses `render_layer="ui"`

## Run

```bash
mini-arcade run --example entity/z_index_and_layer_intuition
mini-arcade run --example entity/z_index_and_layer_intuition --pass-through --backend pygame
mini-arcade run --example entity/z_index_and_layer_intuition --pass-through --backend native
```

## Key idea

Use `z_index` for relationships within one layer. Use `render_layer` only when
the entity belongs to a different pass entirely.

## Related concepts

- [Shapes and Layering Internals](../../concepts/shapes_layers.md)
- [Window and Viewport Internals](../../concepts/window_viewports.md)

## Next step

- [entity/sprite_texture_basics](sprite_texture_basics.md)

