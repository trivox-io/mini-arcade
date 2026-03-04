# 002 - Hello Overlay

## Goal

Render a basic UI/debug overlay over gameplay output.

## What this example does

- Draws text in screen space
- Shows scene/backend/performance info
- Demonstrates overlay rendering order (UI on top of world)

## Run

From repo root:

```bash
python -m mini_arcade.main run --example 002_hello_overlay
```

## Concepts covered

- UI-oriented rendering
- Text measurement and draw operations
- Lightweight runtime debug feedback

## Current limitation

The shared example runner currently does not parse passthrough args into
`build_example(**kwargs)`, so backend selection via forwarded flags is not yet
wired at tutorial level.
