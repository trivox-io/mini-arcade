# entity/animation_frames_basics

## Goal

Understand how frame-based animation works on entities and why it needs a tick
system.

## Why this tutorial exists

An animation component is not magic by itself. It stores:

- `frames`
- `fps`
- `loop`
- current frame index/time

Something still has to call `anim.step(dt)` every frame. This example keeps the
setup minimal and shows two loops with different playback speeds.

## Source map

- Settings profile:
  `examples/settings/entity/animation_frames_basics.yml`
- Example builder:
  `examples/catalog/entity/animation_frames_basics/main.py`
- Scene:
  `examples/catalog/entity/animation_frames_basics/scenes/scene.py`
- Shared animation system:
  `examples/catalog/entity/_shared.py`

## What to verify

You should see:

1. one looping animation at `fps=6`
2. another looping animation at `fps=12`
3. a static sprite using a single frame for comparison
4. the panel updating the current fast-loop frame index

## Run

```bash
mini-arcade run --example entity/animation_frames_basics
mini-arcade run --example entity/animation_frames_basics --pass-through --backend pygame
mini-arcade run --example entity/animation_frames_basics --pass-through --backend native
```

## Key idea

Rendering uses the cached `anim.texture`, but simulation owns advancing the
animation timeline.

## Related concepts

- [Sprites and Animations Internals](../../concepts/sprites_animations.md)
- [Scene Internals](../../concepts/scenes_internals.md)

## Next step

- Future systems tutorials in Group D build on this animation stepping pattern.

