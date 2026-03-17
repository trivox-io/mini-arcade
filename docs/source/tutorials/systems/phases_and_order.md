# systems/phases_and_order

## Goal

Understand how `SystemPipeline` sorts systems by `(phase, order, name)` and
see the execution order visualized on screen.

## Why this tutorial exists

The system pipeline is the backbone of per-frame simulation.  Each system
declares a `SystemPhase` and an `order` integer.  The pipeline auto-sorts
them so that:

- INPUT systems run first
- CONTROL systems run second
- SIMULATION systems run third
- PRESENTATION systems run fourth
- RENDERING systems run last

Within a phase, lower `order` values run first.  Ties are broken by name.

This example creates 10 randomly shuffled systems spanning all five phases
and renders a timeline showing their actual execution order.

## Source map

- Settings profile:
  `examples/settings/systems/phases_and_order.yml`
- Example builder:
  `examples/catalog/systems/phases_and_order/main.py`
- Scene:
  `examples/catalog/systems/phases_and_order/scenes/scene.py`
- Shared runner:
  `examples/_shared/runner.py`

## What to verify

You should see:

1. a vertical list of 10 systems with phase labels and order numbers
2. each system lights up briefly when it runs during the frame
3. the order is always sorted: INPUT → CONTROL → SIMULATION → PRESENTATION
   → RENDERING

Behavior checks:

- reloading the scene keeps the same sorted order (deterministic)
- the phase colors match the legend at the top
- systems within the same phase appear in ascending order

## Run

```bash
mini-arcade run --example systems/phases_and_order
mini-arcade run --example systems/phases_and_order --pass-through --backend pygame
mini-arcade run --example systems/phases_and_order --pass-through --backend native
```

## Common mistakes

- Assuming systems run in registration order — they don't, the pipeline sorts
  them.
- Setting `order` to the same value for two systems and being surprised by
  alphabetical tiebreaking.
- Putting rendering logic in a SIMULATION-phase system — it will run before
  the render phase.

## Related concepts

- [Scene Internals](../../concepts/scenes_internals.md)

## Next step

- [systems/pause_intent_builtin](pause_intent_builtin.md)
