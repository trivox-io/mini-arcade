# entity/sprite_texture_basics

## Goal

Understand how sprite textures override shape rendering and still respect the
entity transform.

## Why this tutorial exists

Once a sprite exists on an entity, the renderer stops using the shape fallback
and draws the texture instead. That means:

- the entity transform still controls size and rotation
- the sprite becomes the visible representation
- shape/style become fallback data when no sprite or animation is present

## Source map

- Settings profile:
  `examples/settings/entity/sprite_texture_basics.yml`
- Example builder:
  `examples/catalog/entity/sprite_texture_basics/main.py`
- Scene:
  `examples/catalog/entity/sprite_texture_basics/scenes/scene.py`
- Procedural texture helpers:
  `examples/catalog/entity/_textures.py`

## What to verify

You should see:

1. a checker texture scaled up through entity size
2. a stretched stripe texture
3. a rotating diamond sprite
4. a plain white block that still renders from shape + style

## Run

```bash
mini-arcade run --example entity/sprite_texture_basics
mini-arcade run --example entity/sprite_texture_basics --pass-through --backend pygame
mini-arcade run --example entity/sprite_texture_basics --pass-through --backend native
```

## Key idea

The scene generates textures procedurally, uploads them through the backend
render port, and stores the resulting texture ids on `entity.sprite.texture`.

## Related concepts

- [Entities Internals](../../concepts/entities.md)
- [Sprites and Animations Internals](../../concepts/sprites_animations.md)

## Next step

- [entity/animation_frames_basics](animation_frames_basics.md)

