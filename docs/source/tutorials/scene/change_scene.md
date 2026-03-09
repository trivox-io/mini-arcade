# scene/change_scene

## Goal

Understand and verify how `ChangeSceneCommand` works at runtime:

- how input enqueues a scene-change command
- how `SceneAdapter.change()` replaces the active stack
- why scene-local state resets after each transition

## Why this tutorial exists

Scene transitions are a core control flow in games (menu -> gameplay, restart,
game over, back to menu). This tutorial isolates transition behavior without
menu systems or gameplay systems.

## Source map

- Settings profile:
  `examples/settings/scene/change_scene.yml`
- Example builder:
  `examples/catalog/scene/change_scene/main.py`
- Scene implementations:
  `examples/catalog/scene/change_scene/scenes/scene.py`
- Core command:
  `packages/mini-arcade-core/src/mini_arcade_core/engine/commands.py`
- Core stack manager:
  `packages/mini-arcade-core/src/mini_arcade_core/engine/scenes/scene_manager.py`

## Runtime flow (actual)

This example reads numeric key presses and enqueues:

- `ChangeSceneCommand("change_scene_hub")`
- `ChangeSceneCommand("change_scene_arena")`
- `ChangeSceneCommand("change_scene_lab")`

`ChangeSceneCommand.execute(...)` calls:

```python
context.managers.scenes.change(self.scene_id)
```

Current `SceneAdapter.change(...)` behavior:

1. `clean()` pops all scenes in stack (`on_exit()` called).
2. `push(scene_id, as_overlay=False)` creates and enters new scene instance.

Because of this, scene-local variables reset on every transition.

## What this example proves

Each scene displays:

- `scene_id`
- `instance_id` (global monotonic id across scene creations)
- `instance_frames`
- `instance_elapsed`
- visible stack summary

When you press `1`, `2`, or `3`, `instance_id` changes and counters reset,
demonstrating full scene replacement, not scene reuse.

## Run

Default:

```bash
mini-arcade run --example scene/change_scene
```

Force pygame:

```bash
mini-arcade run --example scene/change_scene --pass-through --backend pygame
```

Force native:

```bash
mini-arcade run --example scene/change_scene --pass-through --backend native
```

## Controls

- `1` -> `change_scene_hub`
- `2` -> `change_scene_arena`
- `3` -> `change_scene_lab`
- `F1` -> toggle built-in debug overlay
- `ESC` -> quit

## What to verify

1. `1/2/3` always transitions to the target scene.
2. stack summary shows a single base scene after each change.
3. `instance_id` increases after each transition.
4. `instance_frames` restarts from low values after each transition.
5. overlay toggle (`F1`) still works independently.

## Common mistakes

- expecting `change` to preserve scene-local state:
  it does not; state resets because scene instance is recreated
- using `change` where overlay behavior is needed:
  use `push(..., as_overlay=True)` for pause/modal overlays
- forgetting to include scene discovery packages in config

## Related concepts

- Scene transition internals:
  [../../concepts/scene_transitions.md](../../concepts/scene_transitions.md)
- Scene stack internals:
  [../../concepts/scenes_internals.md](../../concepts/scenes_internals.md)
- Menu scene patterns (where change is often triggered):
  [../../concepts/menu_scenes.md](../../concepts/menu_scenes.md)

## Next step

- Keep scene instance but freeze it with overlay policy:
  [pause_overlay_policy.md](pause_overlay_policy.md)
