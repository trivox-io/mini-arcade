# entity/shape_primitives_gallery

## Goal

See the built-in shape kinds side by side and understand how fill, stroke, and
rotation affect them.

## Why this tutorial exists

Mini Arcade can render several entity shapes without custom draw code. This
example makes the supported primitives explicit:

- `rect`
- `circle`
- `triangle`
- `line`
- `poly`

## Source map

- Settings profile:
  `examples/settings/entity/shape_primitives_gallery.yml`
- Example builder:
  `examples/catalog/entity/shape_primitives_gallery/main.py`
- Scene:
  `examples/catalog/entity/shape_primitives_gallery/scenes/scene.py`
- Built-in queued renderer:
  `packages/mini-arcade-core/src/mini_arcade_core/scenes/systems/builtins/__init__.py`

## What to verify

You should see:

1. a filled rounded rectangle
2. a filled circle
3. an outlined rotating triangle
4. a dashed line
5. a polygon rendered from `shape.points`

## Run

```bash
mini-arcade run --example entity/shape_primitives_gallery
mini-arcade run --example entity/shape_primitives_gallery --pass-through --backend pygame
mini-arcade run --example entity/shape_primitives_gallery --pass-through --backend native
```

## Key idea

The scene does not implement custom geometry drawing. It creates entities and
lets the built-in queued renderer choose the correct draw operation for each
shape.

## Related concepts

- [Entities Internals](../../concepts/entities.md)
- [Shapes and Layering Internals](../../concepts/shapes_layers.md)

## Next step

- [entity/z_index_and_layer_intuition](z_index_and_layer_intuition.md)

