# 003 - Simple Shape

## Goal

Render a single entity-driven primitive via the queued render system.

## What this example does

- Builds a `MinWorld` with one rectangle entity
- Uses `BaseQueuedRenderSystem` to push world-layer draw ops
- Returns a `RenderPacket` through scene tick context

## Run

From repo root:

```bash
python -m mini_arcade.main run --example 003_simple_shape
```

## Concepts covered

- Entity + transform + shape data model
- Render queue usage (`rq.rect`, `rq.line`, etc.)
- Minimal scene/system composition
