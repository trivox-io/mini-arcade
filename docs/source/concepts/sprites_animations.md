# Sprites and Animations Internals

## Purpose

Explain how texture-backed entities and frame animations fit into the same
entity/render pipeline as shape-only entities.

## Core files

- `packages/mini-arcade-core/src/mini_arcade_core/engine/components.py`
- `packages/mini-arcade-core/src/mini_arcade_core/engine/animation.py`
- `packages/mini-arcade-core/src/mini_arcade_core/scenes/systems/builtins/__init__.py`

## Sprite component

`Sprite2D` is just:

- one texture id

If it exists on the entity, the built-in renderer draws that texture using the
entity transform for:

- position
- size
- rotation

## Animation component

`Anim2D` wraps an `Animation` object and caches the current frame texture.

Important detail:

- the renderer only draws the current cached texture
- a simulation system must call `anim.step(dt)` to advance frames

## Runtime flow

1. create or load textures
2. store ids in `sprite.texture` or `anim.frames`
3. advance `Anim2D` in a system if animation is used
4. built-in rendering picks `anim.texture` first, then `sprite.texture`

## Tutorial references

- `docs/source/tutorials/entity/sprite_texture_basics.md`
- `docs/source/tutorials/entity/animation_frames_basics.md`

