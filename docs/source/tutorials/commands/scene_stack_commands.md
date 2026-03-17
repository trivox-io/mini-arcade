# commands/scene_stack_commands

## Goal

Understand the built-in scene-stack commands — Push, Pop, and Change — and
see them navigate between three scenes.

## Why this tutorial exists

Scene navigation is driven entirely by commands.  The engine provides:

- **PushSceneCommand** — pushes a new scene onto the stack (previous scene
  stays underneath)
- **PopSceneCommand** — pops the top scene, returning to the one below
- **ChangeSceneCommand** — replaces the current scene entirely

This example wires three scenes and lets you trigger each command type with
keyboard shortcuts.

## Source map

- Settings profile:
  `examples/settings/commands/scene_stack_commands.yml`
- Example builder:
  `examples/catalog/commands/scene_stack_commands/main.py`
- Scene:
  `examples/catalog/commands/scene_stack_commands/scenes/scene.py`
- Shared runner:
  `examples/_shared/runner.py`

## What to verify

You should see:

1. **Main scene** (blue) — press `O` to push an overlay, `C` to change to
   an alternate scene
2. **Overlay scene** (green, semi-transparent) — press `Backspace` to pop
   back to the main scene
3. **Alternate scene** (red) — press `Backspace` to change back to main

Behavior checks:

- pushing the overlay does not destroy the main scene underneath
- popping returns to the exact state the main scene was in
- changing to the alternate scene removes the main scene from the stack
- the stack depth indicator updates correctly

## Controls

| Key | Action |
|-----|--------|
| `O` | Push overlay |
| `C` | Change to alternate |
| `Backspace` | Pop / go back |
| `ESC` | Quit |

## Run

```bash
mini-arcade run --example commands/scene_stack_commands
mini-arcade run --example commands/scene_stack_commands --pass-through --backend pygame
mini-arcade run --example commands/scene_stack_commands --pass-through --backend native
```

## Common mistakes

- Popping when only one scene is on the stack — causes the engine to quit or
  error.
- Using Change when you mean Push — the previous scene is lost.
- Registering scenes in a separate package that isn't in
  `discover_packages`.

## Related concepts

- [Scene Internals](../../concepts/scenes_internals.md)
- [Scene Transitions Internals](../../concepts/scene_transitions.md)

## Next step

- [commands/cheat_sequences](cheat_sequences.md)
