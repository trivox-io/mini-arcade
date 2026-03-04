# 001 - Min Scene

## Goal

Prove engine boot and scene loop wiring with the smallest runnable example.

## What this example does

- Discovers and registers a minimal scene package
- Builds a backend via shared example defaults
- Starts the game loop at scene `min`
- Keeps the window responsive until exit

## Run

From repo root:

```bash
python -m mini_arcade.main run --example 001_min_scene
```

## Concepts covered

- Scene discovery (`SceneRegistry.discover`)
- `ExampleSpec` + shared runner flow
- Baseline `SimScene` lifecycle (`on_enter`, `tick`)
