# scene/pause_overlay_policy

## Goal

Understand how overlay `ScenePolicy` creates a true pause behavior:

- gameplay scene remains visible
- gameplay scene stops updating
- gameplay scene stops receiving input
- pause overlay receives input and controls resume/quit

## Why this tutorial exists

Most games need a pause menu. This tutorial isolates the exact policy and
command wiring used in shipped games (`deja-bounce`, `asteroids`,
`space-invaders`) without gameplay complexity.

## Source map

- Settings profile:
  `examples/settings/scene/pause_overlay_policy.yml`
- Example builder:
  `examples/catalog/scene/pause_overlay_policy/main.py`
- Play scene:
  `examples/catalog/scene/pause_overlay_policy/scenes/play.py`
- Pause scene:
  `examples/catalog/scene/pause_overlay_policy/scenes/pause.py`
- Pause/resume commands:
  `examples/catalog/scene/pause_overlay_policy/scenes/commands.py`
- Core stack manager:
  `packages/mini-arcade-core/src/mini_arcade_core/engine/scenes/scene_manager.py`

## Runtime flow (actual)

1. In play scene, `P` or `ESC` enqueues `PauseOverlayCommand`.
2. `PauseOverlayCommand` executes `PushSceneIfMissingCommand` with:

```python
ScenePolicy(
    blocks_update=True,
    blocks_input=True,
    is_opaque=False,
    receives_input=True,
)
```

3. Pause scene (`BaseMenuScene`) is pushed as overlay and receives input.
4. Underlying play scene remains visible, but does not tick or process input.
5. Resume action removes overlay via `ResumeOverlayCommand`.

## What this example proves

The play scene renders frame/elapsed counters and an animated bar.

When pause overlay is active:

- counters stop increasing
- bar animation freezes
- underlying scene does not react to input
- pause menu handles `UP/DOWN/ENTER/ESC`

After resume, play scene continues from same state (no reset), proving this is
overlay pause, not scene replacement.

## Run

Default:

```bash
mini-arcade run --example scene/pause_overlay_policy
```

Force pygame:

```bash
mini-arcade run --example scene/pause_overlay_policy --pass-through --backend pygame
```

Force native:

```bash
mini-arcade run --example scene/pause_overlay_policy --pass-through --backend native
```

## Controls

Play scene:

- `P` or `ESC` -> push pause overlay
- `F1` -> debug overlay toggle

Pause overlay:

- `UP/DOWN` -> move menu selection
- `ENTER` -> select `CONTINUE` or `QUIT`
- `ESC` -> resume (`quit_command` override)
- `F1` -> debug overlay toggle

## What to verify

1. pause overlay appears on top of gameplay when `P`/`ESC` is pressed.
2. gameplay visuals remain visible under translucent overlay.
3. gameplay counters/animation freeze while overlay is active.
4. `ESC` in pause overlay resumes gameplay.
5. selecting `QUIT` exits game.

## Common mistakes

- using `ChangeSceneCommand` for pause:
  that resets scene state instead of pausing in-place
- forgetting `blocks_update=True`:
  gameplay continues running under pause menu
- forgetting `blocks_input=True`:
  gameplay still reacts to keys while pause menu is open
- forgetting `receives_input=True` on overlay:
  pause menu cannot be navigated

## Related concepts

- Overlay policy internals:
  [../../concepts/overlay_policies.md](../../concepts/overlay_policies.md)
- Scene transitions internals:
  [../../concepts/scene_transitions.md](../../concepts/scene_transitions.md)
- Menu scenes internals:
  [../../concepts/menu_scenes.md](../../concepts/menu_scenes.md)

