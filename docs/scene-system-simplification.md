# Scene System Simplification

## Status

Phase 1 has now been implemented in core and migrated in all three gameplay
scenes:

- `ConfiguredActionIntentSystem`
- `IntentCommandSystem`
- `GameSceneSystemsConfig`
- `extra_system_factories` support for scene-specific auto systems
- Pong auto-system wiring moved from `build_auto_systems()` to scene metadata
- Space Invaders auto-system wiring moved from `build_auto_systems()` to scene
  metadata
- Asteroids auto-system wiring moved from `build_auto_systems()` to scene
  metadata
- Pong, Space Invaders, and Asteroids input bindings now resolve from YAML
  instead of `DEFAULT_*_ACTIONS`

Phase 2 is now implemented in core and migrated in the low-risk renderers:

- `RenderOverlay`
- `EntityRenderRule`
- `ConfiguredQueuedRenderSystem`
- Pong render composition moved from imperative `emit(...)` code to declarative
  overlays
- Space Invaders render composition moved from imperative `emit(...)` and
  `emit_entity(...)` code to declarative overlays plus one entity rule

Phase 3 is now implemented for the built-in vector path and Asteroids:

- built-in queued rendering now supports rotation-aware `triangle`, `line`, and
  `poly` entity rendering
- entity style parsing now normalizes typed fill/stroke data instead of relying
  on raw tuples and dicts
- Asteroids asteroids now render from entity `shape.points` plus stroke style
- Asteroids ship now renders from built-in triangle rendering plus a small
  thrust-only override
- Asteroids render system is reduced to HUD composition and ship-thrust logic

## Validation

The simplification changes have now been validated against the shipped examples
and games with automated smoke coverage.

- added a headless smoke test in
  `packages/mini-arcade-core/tests/test_smoke_examples_and_games.py`
- the smoke pass loads every catalog example entrypoint and runs it through the
  real engine loop with a fake backend for a small number of frames
- the smoke pass also loads all shipped games and runs both menu and gameplay
  scenes for:
  - `deja-bounce`
  - `space-invaders`
  - `asteroids`
  - `office-horrors`
- this validates scene discovery, `on_enter()`, `GameScene` auto-system
  installation, input processing, rendering, and the current startup path after
  the Phase 1-3 changes

Supporting cleanup made during validation:

- `games/office-horrors/src/office_horrors/app.py` was updated to use the
  current `Settings` + `run_game(...)` bootstrap path
- root `pyproject.toml` now sets pytest `--import-mode=importlib` so package
  test modules with repeated names do not collide during collection

## Debug Overlay

The built-in debug overlay is now opt-in and settings-driven.

- it is disabled unless `gameplay.debug_overlay.enabled: true` is present in
  the active settings profile
- examples now receive `gameplay_config` from `Settings.for_example(...)`, so
  example YAML can enable the same overlay path as real games
- the overlay can be configured from YAML for:
  - `title`
  - `toggle_key`
  - `start_visible`
  - `sections`
  - `static_lines`
  - `style`

Scene authors can also extend the overlay without replacing it by overriding:

```python
def debug_overlay_lines(self) -> list[str]:
    return [
        "custom: value",
        "another metric: 42",
    ]
```

Those scene-provided lines are collected by the built-in overlay when the
`scene` section is enabled.

## Current execution model

System execution is already centralized and deterministic:

- `SceneAdapter.push()` creates the scene and calls `on_enter()` before the scene is used.
- `GameScene.tick()` lazily installs scene-defined auto systems.
- `SimScene.tick()` lazily installs capture controls, builds the tick context, runs the system pipeline, and requires a render packet.
- `SystemPipeline` sorts systems by `(phase, order, name, class)` and runs them in sequence.

That means the framework already owns the lifecycle. The remaining boilerplate is mostly scene authors manually describing common framework wiring.

## What is duplicated today

### 1. Input bindings are declared twice

All three gameplay scenes do the same thing:

- define `DEFAULT_*_ACTIONS` in Python
- read `context.settings.controls`
- call `action_map_from_controls_config(...)`
- pass the resulting `ActionMap` into a one-off input system

This is duplicated in:

- `deja-bounce` Pong
- `space-invaders`
- `asteroids`

The YAML files already contain the effective bindings for those games, so the framework is forcing authors to maintain two sources of truth.

### 2. Auto-system registration is still scene boilerplate

Each scene overrides `build_auto_systems()` only to assemble the same category of systems:

- input
- pause
- optional gameplay hotkeys
- render

The framework already auto-installs capture hotkeys globally. It should do the same for the common gameplay scene stack.

### 3. Pause systems are mostly wrappers

`PongPauseSystem` and `AsteroidsPauseSystem` are just `IntentPauseSystem(...)` with a scene-specific command factory and name.

That means the real abstraction already exists, but it is not exposed at the scene configuration level.

### 4. Render systems are partly generic, partly still hand-wired

`BaseQueuedRenderSystem` already supports:

- rects
- lines
- circles
- polygons
- textures
- text
- custom draw calls

So the rendering substrate is not the problem. The gap is that scene authors still need to create a render-system subclass just to register:

- a few custom overlays
- a few entity-specific render overrides
- a HUD

### 5. Gameplay hotkeys are inconsistent

There are two patterns today:

- reusable capture hotkeys installed by the framework
- scene-local hotkey systems that map intent fields to commands or side effects

Pong hotkeys are simple command dispatch and should be declarative. Space Invaders has a mixed case: one part is a gameplay hotkey, another part is ship explosion lifecycle update, which should likely be split.

## Scene-by-scene observations

### Pong

Good candidate for maximum simplification.

- Input bindings are fully representable in YAML.
- Pause is generic.
- Hotkeys are just `intent -> command`.
- Render is default entity rendering plus two overlays (`score`, `trail`).

Pong should not need a custom input system constructor, a custom pause-system class, or a custom hotkeys-system class.

### Space Invaders

Needs more custom gameplay systems, but the common shell is still repetitive.

- Input binding duplication is identical to Pong.
- Pause is generic.
- The render system mostly adds overlays and one alien-explosion override.
- `SpaceInvadersHotkeysSystem` currently mixes a true hotkey (`ship_kill_switch`) with ongoing ship explosion state maintenance.

This scene should keep its gameplay systems, but the framework should absorb the setup work around them.

### Asteroids

The biggest render gap shows up here.

- Input binding duplication is identical.
- Pause is generic.
- Render is custom mostly because polygon entities need rotation-aware rendering and outline-only support.

If core entity rendering understood rotated polygon entities better, Asteroids could avoid most of its custom render-system logic too.

## Proposed direction

### 1. Make scene input declarative

Add a built-in configured action-intent system that resolves bindings directly from gameplay settings.

Suggested shape:

```python
class ConfiguredActionIntentSystem(ActionIntentSystem[TContext, TIntent]):
    def __init__(
        self,
        *,
        controls: Mapping[str, Any],
        scene_key: str,
        intent_factory: Callable[[ActionSnapshot, TContext], TIntent],
        fallback_bindings: Mapping[str, Any] | None = None,
        name: str = "action_intent",
        channel: str | None = "player_1",
    ): ...
```

Rules:

- YAML is the primary source of truth.
- `fallback_bindings` is optional, not mandatory.
- if neither YAML nor fallback bindings exist, fail clearly during scene startup.

Result:

- remove `DEFAULT_PONG_ACTIONS`
- remove `DEFAULT_SPACE_INVADERS_ACTIONS`
- remove `DEFAULT_ASTEROIDS_ACTIONS`
- remove `build_*_action_map()` wrappers

The only code each game should keep is the intent transformation from `ActionSnapshot` to its own intent dataclass.

### 2. Replace `build_auto_systems()` with scene metadata

`GameScene` should be able to auto-compose the common shell from class attributes.

Suggested shape:

```python
@dataclass(frozen=True)
class SceneSystemsConfig:
    controls_scene_key: str | None = None
    input_system_factory: Callable[[RuntimeContext], BaseSystem] | None = None
    pause_command_factory: Callable[[object], object] | None = None
    pause_intent_attr: str = "pause"
    intent_command_bindings: Mapping[str, Callable[[object], object]] = field(default_factory=dict)
    render_factory: Callable[[RuntimeContext], BaseSystem] | None = None
```

Then a gameplay scene becomes:

```python
class PongScene(GameScene[...]):
    systems_config = SceneSystemsConfig(
        controls_scene_key="pong",
        input_system_factory=lambda ctx: PongInputSystem.from_settings(ctx.settings.controls),
        pause_command_factory=lambda _ctx: PauseGameCommand(),
        intent_command_bindings={
            "toggle_trail": lambda _ctx: ToggleTrailCommand(),
            "toggle_slow_mo": lambda _ctx: ToggleSlowMoCommand(),
        },
        render_factory=lambda _ctx: PongRenderSystem(),
    )
```

And eventually even that can shrink further if input/render become declarative enough.

### 3. Add a generic `IntentCommandSystem`

Pong's hotkeys are not special. They are:

- inspect `ctx.intent`
- if field is truthy, push a command

That should be one reusable built-in:

```python
@dataclass
class IntentCommandSystem(BaseSystem[TContext]):
    bindings: Mapping[str, Callable[[TContext], object]]
```

This removes one-off hotkey systems for:

- Pong trail toggle
- Pong slow-mo toggle
- similar future gameplay toggles

For systems that mutate world state every frame, keep custom systems. For one-shot command dispatch, use the generic one.

### 4. Make render composition declarative instead of subclass-first

Keep `BaseQueuedRenderSystem`, but add a composition layer above it.

Suggested pieces:

- `RenderOverlay`: emits queue ops or a custom draw callable
- `EntityRenderRule`: predicate + emitter override
- `ConfiguredQueuedRenderSystem`: default entity renderer + registered overlays + optional entity overrides

Suggested shape:

```python
@dataclass(frozen=True)
class EntityRenderRule:
    matches: Callable[[BaseEntity, object], bool]
    emit: Callable[[object, RenderQueue, BaseEntity], None]


@dataclass(frozen=True)
class RenderOverlay:
    emit: Callable[[object, RenderQueue], None]


class ConfiguredQueuedRenderSystem(BaseQueuedRenderSystem[TContext]):
    overlays: tuple[RenderOverlay, ...] = ()
    entity_rules: tuple[EntityRenderRule, ...] = ()
```

What this buys:

- Pong only registers `score` and `trail` overlays.
- Space Invaders registers a small set of overlays plus one alien explosion override.
- authors stop writing a custom render-system class unless they truly need custom orchestration.

### 5. Improve the built-in entity renderer for rotated/vector entities

This is the change that helps Asteroids the most.

Core renderer improvements:

- support `rotation_deg` for `poly`, `line`, and `triangle` entity shapes
- support outline-only polygon rendering explicitly
- respect stroke/thickness metadata consistently
- allow per-entity render layer without custom renderer code

If those exist, Asteroids entities can become data-driven:

- ship: triangle/poly entity with rotation and optional thrust overlay
- asteroid: polygon entity with rotation
- bullet: tiny rect/circle entity

Then the scene only adds HUD and any special transient overlay.

### 6. Separate hotkeys from gameplay state machines

`SpaceInvadersHotkeysSystem` should likely be split into:

- `IntentCommandSystem` or `IntentCallbackSystem` for `ship_kill_switch`
- a regular `ShipExplosionLifecycleSystem` that updates animation/timers every frame

That separation makes the framework abstraction cleaner:

- hotkeys are one-shot triggers
- gameplay systems own ongoing simulation

## Recommended implementation order

### Phase 1: low-risk boilerplate reduction

- add `ConfiguredActionIntentSystem`
- add `IntentCommandSystem`
- add class-level gameplay scene metadata and let `GameScene` auto-install those systems
- migrate Pong first

This removes the most boilerplate with minimal engine risk.

### Phase 2: render composition

- add `ConfiguredQueuedRenderSystem`
- add overlay registration and entity override rules
- migrate Pong and Space Invaders render systems

This keeps `RenderQueue` and `RenderPacket` unchanged while simplifying scene code.

### Phase 3: better vector entity rendering

- add rotation-aware polygon/line rendering in the built-in entity renderer
- model Asteroids ship/asteroids more declaratively
- reduce Asteroids render system to HUD-only or near-HUD-only

## Expected outcome

After these changes, a simple game scene should usually only need:

- a world builder in `on_enter()`
- its gameplay systems
- one intent factory
- optional overlay emitters

It should not need to manually wire:

- action-map loading
- pause system wrappers
- one-shot hotkey systems
- a render-system subclass just to attach two overlays

## Bottom line

Mini Arcade already has the right primitives. The missing layer is a declarative composition API on top of them.

The biggest win is not replacing the system pipeline. It is stopping scene authors from re-assembling the same input, pause, hotkey, and render shell in every game.
