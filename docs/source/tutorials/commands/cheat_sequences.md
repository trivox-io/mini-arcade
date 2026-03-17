# commands/cheat_sequences

## Goal

Implement a cheat-code manager that detects specific key sequences and
triggers game-altering effects.

## Why this tutorial exists

Classic games often have hidden key sequences (Konami code, etc.) that
unlock special modes.  This tutorial shows how to build a `CheatManager`
that:

- buffers recent key presses
- matches them against registered cheat patterns
- fires callbacks when a sequence completes
- displays active cheat status on a panel

## Source map

- Settings profile:
  `examples/settings/commands/cheat_sequences.yml`
- Example builder:
  `examples/catalog/commands/cheat_sequences/main.py`
- Scene:
  `examples/catalog/commands/cheat_sequences/scenes/scene.py`
- Shared runner:
  `examples/_shared/runner.py`

## What to verify

You should see:

1. a status panel showing registered cheat codes and their activation state
2. typing the correct key sequence (shown on screen) activates the cheat
3. an activation flash confirms the match
4. active cheats display as "ON" in the panel

Example sequences (from the demo):

- `G O D` — toggles god mode
- `Up Up` — toggles double jump
- `F A S T` — toggles speed boost

Behavior checks:

- partial sequences don't trigger (typing `G O` then `X` resets the buffer)
- activating the same cheat again toggles it off
- the key buffer has a maximum length and drops old keys

## Controls

| Keys | Cheat |
|------|-------|
| `G O D` | God mode |
| `Up Up` | Double jump |
| `F A S T` | Speed boost |
| `ESC` | Quit |

## Run

```bash
mini-arcade run --example commands/cheat_sequences
mini-arcade run --example commands/cheat_sequences --pass-through --backend pygame
mini-arcade run --example commands/cheat_sequences --pass-through --backend native
```

## Common mistakes

- Not clearing the key buffer between scenes — old keys leak into new
  sequences.
- Using `keys_held` instead of `keys_pressed` — held keys repeat every
  frame.
- Making sequences too long — players won't remember them.

## Related concepts

- [Input Coordinate Mapping Internals](../../concepts/input_coordinate_mapping.md)
- [Scene Internals](../../concepts/scenes_internals.md)

## Next step

- [commands/effect_and_debug_hotkeys](effect_and_debug_hotkeys.md)
