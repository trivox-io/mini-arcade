# systems/pause_intent_builtin

## Goal

See how `IntentPauseSystem` detects a pause key press and drives a
pause overlay without any custom input handling code.

## Why this tutorial exists

Pausing a game is a universal requirement.  The built-in
`IntentPauseSystem` handles:

- detecting the pause key (default: `P`)
- toggling a `paused` flag on the scene context
- allowing a pause overlay scene to render on top

This example wires two scenes — a gameplay scene with a bouncing box and a
semi-transparent pause overlay — and lets the built-in system manage the
transition.

## Source map

- Settings profile:
  `examples/settings/systems/pause_intent_builtin.yml`
- Example builder:
  `examples/catalog/systems/pause_intent_builtin/main.py`
- Scene:
  `examples/catalog/systems/pause_intent_builtin/scenes/scene.py`
- Shared runner:
  `examples/_shared/runner.py`

## What to verify

You should see:

1. a bouncing cyan box with a frame counter
2. pressing `P` pauses the simulation — the box freezes
3. a dark overlay with "PAUSED" text appears
4. pressing `P` again resumes the simulation
5. the frame counter only increments while unpaused

## Controls

| Key | Action |
|-----|--------|
| `P` | Toggle pause |
| `ESC` | Quit |

## Run

```bash
mini-arcade run --example systems/pause_intent_builtin
mini-arcade run --example systems/pause_intent_builtin --pass-through --backend pygame
mini-arcade run --example systems/pause_intent_builtin --pass-through --backend native
```

## Common mistakes

- Forgetting to register the overlay scene in the same discover package.
- Manually checking for the pause key when the built-in system already does
  it.
- Not accounting for the paused state in custom systems — they still receive
  `step()` calls unless they check the context flag.

## Related concepts

- [Overlay Policies Internals](../../concepts/overlay_policies.md)
- [Scene Internals](../../concepts/scenes_internals.md)

## Next step

- [systems/animation_tick_builtin](animation_tick_builtin.md)
