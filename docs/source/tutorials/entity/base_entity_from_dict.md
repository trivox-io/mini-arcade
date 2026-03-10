# entity/base_entity_from_dict

## Goal

Understand the minimum data contract needed to create a renderable entity with
`BaseEntity.from_dict(...)`.

## Why this tutorial exists

Before introducing textures, animations, or system-heavy gameplay code, you
need to understand the plain entity payload shape:

- `transform`
- `shape`
- `style`
- `kinematic`
- `collider`
- `z_index`

This tutorial keeps the example small and shows that one dictionary is enough
to produce a moving world object. The courier motion itself now goes through the
built-in movement helpers instead of ad hoc scene math.

## Source map

- Settings profile:
  `examples/settings/entity/base_entity_from_dict.yml`
- Example builder:
  `examples/catalog/entity/base_entity_from_dict/main.py`
- Scene:
  `examples/catalog/entity/base_entity_from_dict/scenes/scene.py`
- Shared entity helpers:
  `examples/catalog/entity/_shared.py`
- Entity core:
  `packages/mini-arcade-core/src/mini_arcade_core/engine/entities.py`

## What to verify

You should see:

1. a cyan rectangle moving and bouncing across the guide line
2. a triangle rendered only from stroke data
3. a circle rendered from shape + style
4. the right-side panel updating the courier position and velocity

## Run

```bash
mini-arcade run --example entity/base_entity_from_dict
mini-arcade run --example entity/base_entity_from_dict --pass-through --backend pygame
mini-arcade run --example entity/base_entity_from_dict --pass-through --backend native
```

## Key idea

The moving courier is built from one plain dictionary:

```python
entity = BaseEntity.from_dict(
    {
        "id": 1,
        "name": "Courier Block",
        "transform": {
            "center": {"x": 56.0, "y": 236.0},
            "size": {"width": 96.0, "height": 56.0},
        },
        "shape": {"kind": "rect"},
        "style": {"fill": [82, 193, 255, 255]},
        "kinematic": {
            "velocity": {"vx": 150.0, "vy": 0.0},
            "max_speed": 150.0,
        },
    }
)
```

That payload is enough for:

- construction
- simulation data attachment
- built-in rendering

The example scene then hands the courier to the shared entity tutorial motion
stack, which uses `KinematicMotionSystem` plus `ViewportConstraintSystem` for
movement and bounds handling.

## Related concepts

- [Entities Internals](../../concepts/entities.md)
- [Shapes and Layering Internals](../../concepts/shapes_layers.md)

## Next step

- [entity/shape_primitives_gallery](shape_primitives_gallery.md)
