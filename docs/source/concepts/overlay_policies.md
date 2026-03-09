# Overlay Policies Internals

## Purpose

Explain how `ScenePolicy` affects rendering, updates, and input routing for
overlay scenes such as pause menus, debug overlays, and modal dialogs.

## Core files

- `packages/mini-arcade-core/src/mini_arcade_core/engine/scenes/models.py`
- `packages/mini-arcade-core/src/mini_arcade_core/engine/scenes/scene_manager.py`
- `packages/mini-arcade-core/src/mini_arcade_core/engine/commands.py`

## ScenePolicy fields

- `blocks_update`:
  stop ticking scenes below this entry
- `blocks_input`:
  stop input routing to scenes below this entry
- `is_opaque`:
  hide rendering of scenes below this entry
- `receives_input`:
  whether this scene can be selected as input owner

## Pause overlay baseline policy

Typical pause overlay policy:

```python
ScenePolicy(
    blocks_update=True,
    blocks_input=True,
    is_opaque=False,
    receives_input=True,
)
```

Result:

- gameplay remains visible
- gameplay simulation is frozen
- gameplay input is blocked
- pause menu receives input

## Built-in debug overlay policy

`ToggleDebugOverlayCommand` uses:

```python
ScenePolicy(
    blocks_update=False,
    blocks_input=False,
    is_opaque=False,
    receives_input=False,
)
```

Result:

- gameplay keeps running
- gameplay keeps receiving input
- overlay is view-only telemetry

## How manager methods apply policy

`SceneAdapter.visible_entries()`:

- renders from top-most opaque scene upward, otherwise full visible stack

`SceneAdapter.update_entries()`:

- ticks from bottom to top, cutting off when a scene blocks update

`SceneAdapter.input_entry()`:

- computes input candidates respecting blockers
- returns top-most candidate with `receives_input=True`

## Real game usage

- `games/deja-bounce/src/deja_bounce/scenes/commands.py`
- `games/asteroids/src/asteroids/scenes/commands.py`
- `games/space-invaders/src/space_invaders/scenes/commands.py`

All three push pause overlays with blocking policy and resume by removing
overlay scene.

## Tutorial reference

- `docs/source/tutorials/scene/pause_overlay_policy.md`

