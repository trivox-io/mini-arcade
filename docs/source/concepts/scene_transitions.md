# Scene Transitions Internals

## Purpose

Explain command-level transition semantics for:

- `ChangeSceneCommand`
- `PushSceneCommand`
- `PopSceneCommand`
- `RemoveSceneCommand`

## Core files

- `packages/mini-arcade-core/src/mini_arcade_core/engine/commands.py`
- `packages/mini-arcade-core/src/mini_arcade_core/engine/scenes/scene_manager.py`
- `packages/mini-arcade-core/src/mini_arcade_core/engine/scenes/models.py`

## `change`: replace current stack

`ChangeSceneCommand(scene_id)` calls `scenes.change(scene_id)`.

Current `SceneAdapter.change(...)` implementation:

1. `clean()`:
   pop all scenes and call `on_exit()`
2. `push(scene_id, as_overlay=False)`:
   create new scene instance and call `on_enter()`

Implication:

- previous stack is discarded
- new scene starts with fresh local state

Use for:

- menu -> gameplay
- restart gameplay from scratch
- back to main menu

## `push`: add scene without discarding stack

`PushSceneCommand(scene_id, as_overlay=...)` appends a new scene entry.

Use with `as_overlay=True` and explicit `ScenePolicy` for:

- pause overlays
- modal dialogs
- debug or tool overlays

Pause-overlay policy details:

- `docs/source/concepts/overlay_policies.md`
- `docs/source/tutorials/scene/pause_overlay_policy.md`

## `pop` / `remove`: unwind overlays or specific scenes

- `PopSceneCommand()` removes top scene
- `RemoveSceneCommand(scene_id)` removes first matching scene from top

Use for:

- close pause overlay
- dismiss temporary modal scene

## Choosing the right transition command

- need full state reset -> `change`
- need temporary layer over current state -> `push` + policy
- need to go back from temporary layer -> `pop` or `remove`

## ScenePolicy interaction

When pushing overlays, `ScenePolicy` controls whether underlying scenes:

- update (`blocks_update`)
- receive input (`blocks_input`)
- remain visible (`is_opaque`)

For `change`, policy on old scenes is irrelevant because stack is cleaned first.

## Tutorial reference

- `docs/source/tutorials/scene/change_scene.md`
