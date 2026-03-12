# Scene Internals

## Purpose

This page explains how scenes are registered, discovered, stacked, ticked, and
rendered internally.

## Registration and discovery

Registration decorator:

- `packages/mini-arcade-core/src/mini_arcade_core/scenes/autoreg.py`

Usage:

```python
from mini_arcade_core.scenes.autoreg import register_scene


@register_scene("minimal_scene")
class MinimalScene(...):
    ...
```

Discovery:

- `packages/mini-arcade-core/src/mini_arcade_core/scenes/registry.py`
- `SceneRegistry.discover(*packages)` imports all modules in each package
- imported modules execute decorators and populate autoreg catalog

If a scene id is missing at runtime, it is usually a discovery/import issue.

## Scene stack and policies

Stack manager:

- `packages/mini-arcade-core/src/mini_arcade_core/engine/scenes/scene_manager.py`

Policy model:

- `packages/mini-arcade-core/src/mini_arcade_core/engine/scenes/models.py`

`ScenePolicy` fields:

- `blocks_update`
- `blocks_input`
- `is_opaque`
- `receives_input`

This controls pause overlays, modal menus, and render visibility.

Overlay policy deep dive:

- `docs/source/concepts/overlay_policies.md`
- `docs/source/tutorials/scene/pause_overlay_policy.md`

## Built-in debug overlay internals

Engine files involved:

- `packages/mini-arcade-core/src/mini_arcade_core/engine/loop/hooks.py`
- `packages/mini-arcade-core/src/mini_arcade_core/engine/commands.py`
- `packages/mini-arcade-core/src/mini_arcade_core/scenes/debug_overlay.py`

Flow:

1. `DefaultGameHooks.on_events(...)` maps `KEYDOWN(F1)` to
   `ToggleDebugOverlayCommand`.
2. `EngineRunner._execute_commands(...)` executes queued commands each frame.
3. `ToggleDebugOverlayCommand` toggles scene id `debug_overlay`:
   - remove if already present
   - otherwise push as overlay with policy:
     - `blocks_update=False`
     - `blocks_input=False`
     - `is_opaque=False`
     - `receives_input=False`
4. `DebugOverlayScene.tick(...)` renders telemetry and stack lines.

Important implications:

- overlay visibility is scene-stack based, not a hardcoded renderer mode
- gameplay scene keeps ticking while debug overlay is visible
- input remains owned by underlying scene because overlay does not receive input
- discovery must include `mini_arcade_core.scenes`, otherwise the toggle command
  cannot instantiate `debug_overlay`

Tutorial reference:

- `docs/source/tutorials/scene/debug_overlay_builtin.md`

## BaseMenuScene internals

Base menu implementation:

- `packages/mini-arcade-core/src/mini_arcade_core/ui/menu.py`

`BaseMenuScene` is a `SimScene` specialization that wires a small system
pipeline for menus:

1. `MenuInputSystem` (`InputFrame` -> `MenuIntent`)
2. `MenuNavigationSystem` (selection index and cooldown)
3. `MenuActionSystem` (enqueue command from selected item)
4. `MenuRenderSystem` (draw menu through UI render queue)

Extension points in subclasses:

- `menu_title`
- `menu_style()`
- `menu_items()`
- optional `quit_command()`

For full details and patterns (main menu vs pause overlay):

- `docs/source/concepts/menu_scenes.md`
- `docs/source/tutorials/scene/menu_scene_base.md`

## Scene transition semantics

The most important stack mutations are:

- `change(scene_id)`:
  full stack replacement (`clean()` + `push()`)
- `push(scene_id, as_overlay=...)`:
  keep current stack and append one scene
- `pop()` / `remove_scene(scene_id)`:
  unwind temporary scenes

Detailed transition behavior and when to use each command:

- `docs/source/concepts/scene_transitions.md`
- `docs/source/tutorials/scene/change_scene.md`

## Scene lifecycle

Base class:

- `packages/mini-arcade-core/src/mini_arcade_core/scenes/sim_scene.py`

Lifecycle methods:

1. `__init__(RuntimeContext)`
2. `on_enter()`
3. `tick(input_frame, dt) -> RenderPacket`
4. `on_exit()`

Typical patterns:

- minimal scene:
  override `tick(...)` directly and return `RenderPacket`
- gameplay scene:
  set `tick_context_type`
  initialize `world` in `on_enter()`
  register systems in pipeline

Current gameplay-scene structure in the reference games:

- `scene.py`: scene registration plus high-level orchestration
- `bootstrap.py`: asset resolution, template loading, and world construction
- `pipeline.py`: ordered system/bundle list builders
- `spawn.py`: typed spawn specs and spawn policies
- `systems/`: atomic processors and feature bundles

## Tick context and system pipeline

Core types (same module):

- `BaseWorld`
- `BaseIntent`
- `BaseTickContext`
- `SystemPipeline`
- `EntityIdDomain`

Gameplay scene shell:

- `packages/mini-arcade-core/src/mini_arcade_core/scenes/game_scene.py`
- `GameSceneSystemsConfig` declaratively installs common gameplay systems for:
  - action-to-intent input
  - pause intent handling
  - one-shot intent-to-command bindings
  - extra scene-specific systems
  - render system wiring

Terminology:

- a **system** is one phase-ordered processor with a single `step(ctx)` job
- a **system bundle** is just a composition helper that expands into multiple
  systems before pipeline ordering

Use bundles when a gameplay feature is made from several atomic processors
(input-to-velocity, motion integration, viewport constraints), instead of
packing those concerns into one large `step(...)` method.

For discrete grid games, prefer the built-in grid toolkit instead of
re-implementing timing and free-cell queries in each scene:

- `CadenceSystem` for logical movement ticks
- `GridBounds` / `GridLayout` for grid-space ownership and rendering
- `GridCellSpawnSystem` for cell-based item spawning

For falling-block scenes, prefer the dedicated board helpers instead of
embedding board collapse and piece layout logic inside scene classes:

- `BlockBoard` for settled-cell state
- `FallingBlockPieceSpec` / `FallingBlockPiece` for active pieces
- `BoardRowClearSystem` for filled-row collapse
- `BagRandomizer` for deterministic piece bags

For brick-breaker scenes, prefer the reusable bounce/brick helpers instead of
repeating ball-vs-paddle and ball-vs-brick logic in each game:

- `ViewportBounceSystem` for wall reflection
- `BounceCollisionSystem` for ball-vs-rect reflection
- `PaddleBouncePolicy` for paddle contact shaping
- `BrickFieldCollisionSystem` for brick damage and removal

Builder pattern used by the reference games:

- world construction usually lives in a local `build_<scene>_world(...)`
  helper in `bootstrap.py`
- gameplay system registration usually lives in a local
  `build_<scene>_systems(...)` helper in `pipeline.py`
- scene `on_enter()` should mostly compose those helpers rather than inline
  entity creation and long system lists

World query model:

- gameplay code should prefer semantic helpers like `world.ship()` or
  `world.aliens()`
- those helpers are usually backed by `BaseWorld.find_entity(...)`,
  `get_entities_by_tag(...)`, and scene-specific convenience methods
- named `entity_id_domains` exist for constrained spawn allocation and tracked
  cleanup, not as the primary gameplay query API

Each frame:

1. scene builds typed tick context
2. pipeline runs systems in order
3. one render system must assign `ctx.packet`
4. scene returns `ctx.packet`

If no render packet is produced, engine raises runtime error.

## Frame loop interaction

Main loop:

- `packages/mini-arcade-core/src/mini_arcade_core/engine/loop/runner.py`

Per frame (simplified):

1. poll backend events
2. build `InputFrame`
3. pick input-focused scene from stack
4. tick update scenes based on scene policy
5. process cheats and command queue
6. collect visible scene packets
7. run render pipeline

Window/viewport details used by scenes and render passes:

- `docs/source/concepts/window_viewports.md`
- `docs/source/concepts/input_coordinate_mapping.md`

## Render paths in scenes

Two common patterns:

1. Direct `RenderPacket` ops in scene `tick` (good for minimal examples)
2. Queued render systems with `RenderQueue` + `DrawCall` + `Drawable` classes
   (good for complex games)
3. Declarative queued rendering via `ConfiguredQueuedRenderSystem`,
   `RenderOverlay`, and `EntityRenderRule` (preferred for medium/large games)

Reference implementations:

- minimal direct packet:
  `examples/catalog/scene/minimal_scene/scenes/scene.py`
- declarative queued render + draw ops:
  `games/deja-bounce/src/deja_bounce/scenes/pong/systems/render.py`
  `games/deja-bounce/src/deja_bounce/scenes/pong/draw_ops.py`
  `games/asteroids/src/asteroids/scenes/asteroids/systems/render.py`
  `games/space-invaders/src/space_invaders/scenes/space_invaders/systems/render.py`

## Common scene failures

- scene not found:
  discovery package missing or scene module not imported
- no render output:
  render system never set `ctx.packet`
- unexpected input routing:
  overlay policy blocks input/update
- overlay render confusion:
  opaque policy hides lower scenes
