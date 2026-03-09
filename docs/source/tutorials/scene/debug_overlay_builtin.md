# scene/debug_overlay_builtin

## Goal

Understand exactly how the built-in debug overlay works, why `F1` toggles it,
and what scene stack/input policy it uses.

## Why this tutorial exists

This is the first scene-stack tutorial that explains a built-in overlay scene
managed by engine commands, not by your game code.

It demonstrates:

- event hook -> command queue -> scene stack flow
- policy behavior (`overlay`, `blocks_update`, `blocks_input`, `receives_input`)
- required scene discovery so `debug_overlay` can be instantiated

## Source map

- Example settings:
  `examples/settings/scene/debug_overlay_builtin.yml`
- Example builder:
  `examples/catalog/scene/debug_overlay_builtin/main.py`
- Example scene:
  `examples/catalog/scene/debug_overlay_builtin/scenes/scene.py`
- Built-in overlay scene:
  `packages/mini-arcade-core/src/mini_arcade_core/scenes/debug_overlay.py`
- F1 hook:
  `packages/mini-arcade-core/src/mini_arcade_core/engine/loop/hooks.py`
- Toggle command:
  `packages/mini-arcade-core/src/mini_arcade_core/engine/commands.py`

## Internal flow (actual runtime path)

When you press `F1`, this is what happens:

1. `DefaultGameHooks.on_events(...)` receives `KEYDOWN(F1)` and enqueues
   `ToggleDebugOverlayCommand`.
2. `EngineRunner` drains command queue in the same frame.
3. `ToggleDebugOverlayCommand.execute(...)`:
   - removes `debug_overlay` if already on stack
   - otherwise pushes scene id `debug_overlay` as overlay with policy:
     - `blocks_update=False`
     - `blocks_input=False`
     - `is_opaque=False`
     - `receives_input=False`
4. `DebugOverlayScene.tick(...)` renders telemetry lines (fps, dt, viewport,
   render stats, stack summary).

No game-specific scene code is needed for this toggle behavior.

## Critical config requirement

Your scene discovery must include:

- your example/game scene package
- `mini_arcade_core.scenes`

This tutorial profile sets both:

```yaml
scene:
  scene_registry:
    discover_packages:
      - examples.catalog.scene.debug_overlay_builtin
      - mini_arcade_core.scenes
```

If `mini_arcade_core.scenes` is missing, pressing `F1` cannot create
`debug_overlay` and overlay toggle appears to do nothing.

## Code excerpt

From `ToggleDebugOverlayCommand`:

```python
if scenes.has_scene("debug_overlay"):
    scenes.remove_scene("debug_overlay")
else:
    scenes.push(
        "debug_overlay",
        as_overlay=True,
        policy=ScenePolicy(
            blocks_update=False,
            blocks_input=False,
            is_opaque=False,
            receives_input=False,
        ),
    )
```

From this tutorial scene (`debug_overlay_builtin`):

```python
stack = list(services.scenes.visible_entries())
input_owner = services.scenes.input_entry()
overlay_active = any(e.scene_id == "debug_overlay" for e in stack)
```

It prints stack + input owner so you can verify policy behavior while toggling.

## Run

Default:

```bash
mini-arcade run --example scene/debug_overlay_builtin
```

Force pygame:

```bash
mini-arcade run --example scene/debug_overlay_builtin --pass-through --backend pygame
```

Force native:

```bash
mini-arcade run --example scene/debug_overlay_builtin --pass-through --backend native
```

## What to verify

1. `F1` shows and hides the built-in telemetry panel.
2. `overlay active` flips `False/True` in the base scene.
3. `input owner scene` remains `debug_overlay_builtin` even when overlay is visible.
4. animation/frame counter continue while overlay is visible
   (`blocks_update=False` on overlay policy).
5. `ESC` exits cleanly.

## Built-in overlay vs game overlays

Use built-in overlay for engine/runtime telemetry during development.

Use game overlays (pause menus, modal UI) when gameplay flow should be blocked.
Reference pause overlays in shipped games:

- `games/deja-bounce/src/deja_bounce/scenes/commands.py`
- `games/asteroids/src/asteroids/scenes/commands.py`
- `games/space-invaders/src/space_invaders/scenes/commands.py`

Those overlays usually set `blocks_update=True` and `blocks_input=True`.

## Related concepts

- Scene stack internals:
  [../../concepts/scenes_internals.md](../../concepts/scenes_internals.md)
- Config/discovery internals:
  [../../concepts/configuration.md](../../concepts/configuration.md)
- Backend internals:
  [../../concepts/backends.md](../../concepts/backends.md)

