# 004 - Shape Gallery

## Goal

Show multiple primitive kinds in one scene using the same queued render flow.

## What this example does

- Spawns entities for rectangle, line, circle, triangle, and polygon
- Emits per-entity draw operations in world layer
- Demonstrates render ordering by entity `z_index`

## Run

From repo root:

```bash
python -m mini_arcade.main run --example 004_shape_gallery
```

## Concepts covered

- Primitive shape variety in one scene
- Shared render system pattern across different shape kinds
- Composition of draw operations without backend-specific code
