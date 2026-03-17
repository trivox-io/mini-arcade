# commands/custom_scene_commands

## Goal

Learn how to define custom `Command` subclasses that execute game-specific
side effects through the scene command queue.

## Why this tutorial exists

The command pattern decouples "what should happen" from "when it happens".
Instead of mutating state inline during `tick()`, you enqueue command objects
that the scene processes after the simulation step.  This tutorial shows:

- defining `AddScoreCommand` and `ResetCounterCommand` as `Command`
  subclasses
- enqueuing them from a system or tick handler
- a log panel that records every executed command

## Source map

- Settings profile:
  `examples/settings/commands/custom_scene_commands.yml`
- Example builder:
  `examples/catalog/commands/custom_scene_commands/main.py`
- Scene:
  `examples/catalog/commands/custom_scene_commands/scenes/scene.py`
- Shared runner:
  `examples/_shared/runner.py`

## What to verify

You should see:

1. a score counter that increments when you press `Space`
2. pressing `R` enqueues a `ResetCounterCommand` that zeroes the score
3. a scrolling log panel showing each command as it executes
4. the log entries include timestamps

## Controls

| Key | Action |
|-----|--------|
| `Space` | Add score +10 |
| `R` | Reset counter |
| `ESC` | Quit |

## Run

```bash
mini-arcade run --example commands/custom_scene_commands
mini-arcade run --example commands/custom_scene_commands --pass-through --backend pygame
mini-arcade run --example commands/custom_scene_commands --pass-through --backend native
```

## Common mistakes

- Mutating state directly instead of going through commands — bypasses the
  command log and any undo/replay infrastructure.
- Forgetting to register commands with the scene's command processor.
- Creating commands with side effects in `__init__` instead of `execute()`.

## Related concepts

- [Scene Internals](../../concepts/scenes_internals.md)

## Next step

- [commands/scene_stack_commands](scene_stack_commands.md)
