# Shapes and Layering Internals

## Purpose

Explain how built-in shapes, styling, `z_index`, and `render_layer` work
together in queued rendering.

## Core file

- `packages/mini-arcade-core/src/mini_arcade_core/scenes/systems/builtins/__init__.py`

## Built-in shapes

The default queued renderer understands:

- `rect`
- `circle`
- `triangle`
- `line`
- `poly`

`triangle` and normalized `poly` points are rotated and scaled from the entity
transform before being emitted to the render queue.

## Fill and stroke

`RenderStyle` supports:

- `fill`
- `stroke`

Typical behavior:

- fill only:
  solid shape
- stroke only:
  outline shape
- both:
  filled polygon with outline where supported

## `z_index`

`z_index` sorts entities inside one layer. Use it when two world entities
overlap and one should appear above the other.

## `render_layer`

`render_layer` changes the pass the entity is emitted into, for example:

- `world`
- `ui`
- `effects`

This is stronger than `z_index` because it moves the entity to a different pass
entirely.

## Tutorial references

- `docs/source/tutorials/entity/shape_primitives_gallery.md`
- `docs/source/tutorials/entity/z_index_and_layer_intuition.md`

