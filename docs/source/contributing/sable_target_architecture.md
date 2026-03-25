# Sable target architecture

This document defines the target package and module architecture for Sable.

The goal is to simplify the current monorepo structure, make command domains
obvious, and reduce ambiguity around what belongs in `mini_arcade`,
`mini_arcade_core`, and the backend packages.

## Outcome summary

The production-ready direction is:

- `mini_arcade` becomes the implementation package
- `mini_arcade_core` becomes the contracts-only package
- top-level command domains collapse into a smaller set of clear modules
- reusable application logic lives under `mini_arcade.common`
- runtime and gameplay logic moves out of `mini_arcade_core` into dedicated
  implementation domains inside `mini_arcade`

This is intended to be simpler and clearer than the current split between
application code, engine code, and partially migrated modules.

## Design principles

- Keep command entrypoints thin
- Put reusable application logic in `common`
- Put implementation logic in `mini_arcade`, not `mini_arcade_core`
- Keep `mini_arcade_core` stable, small, and protocol-focused
- Keep backend packages unchanged for now
- Avoid top-level `core/` and `backend/` folders in `mini_arcade` for migrated
  implementation code because those names are reserved for future repo-split
  concerns

## Target package roles

### `mini_arcade`

Owns:

- CLI
- command entrypoints
- workspace and project discovery
- scaffolding
- engine and runtime implementation
- scene and system implementation
- UI implementation
- shared application services

This package should be the place where behavior lives.

### `mini_arcade_core`

Owns only:

- protocols
- contracts
- immutable data models
- typed config objects
- enums and shared types
- runtime and backend ports
- cross-package event contracts

This package should not contain major implementation logic.

### `mini_arcade_pygame_backend` / `mini_arcade_native_backend`

Own:

- backend-specific implementations of the contracts from `mini_arcade_core`

These packages are acceptable as-is for this stage.

## Target top-level grouping in `mini_arcade`

```text
mini_arcade/
  app.py
  main.py
  constants.py

  cli/
  commands/
  common/
  engine/
  scenes/
  systems/
  ui/
  spaces/
  backends/
  utils/
```

## Command domains

The target command structure is:

```text
mini_arcade/commands/
  game/
    commands.py
    processors.py
  eg/
    commands.py
    processors.py
  system_lab/
    commands.py
    processors.py
```

This replaces the current pattern of splitting related command behavior across
multiple top-level modules such as `game_runner`, `game_scaffold`,
`system_lab`, and `system_lab_scaffold`.

### `game`

Responsibilities:

- list available games
- distinguish runnable game entries from repo metadata
- run a game by id
- run a game from an explicit source folder
- pass through arguments to the selected game
- scaffold a new game
- support future game tour/help flows if needed

The current distinction between clones and originals should be treated as a
workspace concern, not a command-domain concern.

### `eg`

Responsibilities:

- list available examples
- run an example by id
- tour examples

This should be a first-class command domain instead of being hidden inside the
general runner shape.

### `system_lab`

Responsibilities:

- list experiments
- run experiments
- scaffold experiments

This keeps the lab workflow under one command domain rather than splitting
runtime and scaffold concerns into separate top-level command packages.

## `common` responsibilities

`mini_arcade.common` should own reusable application logic shared across
commands and runtime entrypoints.

Target subdomains:

```text
mini_arcade/common/
  workspace/
  projects/
  settings/
  imports/
  process/
  scaffold/
  files/
```

Examples of logic that belongs here:

- game/example path discovery
- workspace root discovery
- project metadata loading
- settings loading helpers
- scaffold templates and generation helpers
- subprocess launch helpers
- source-root and import-path helpers

Examples of logic that should not live here:

- render pipeline behavior
- scene update logic
- simulation systems
- backend-specific behavior

## Implementation domains to move into `mini_arcade`

The implementation logic currently living in `mini_arcade_core` should be
grouped into the following app-side domains.

### `engine`

Owns:

- game lifecycle
- main loop
- manager implementations
- render pipeline implementation
- capture implementation
- runtime service wiring
- scene runtime orchestration

Suggested grouping:

```text
mini_arcade/engine/
  lifecycle/
  loop/
  render/
  capture/
  input/
  audio/
  scene_runtime/
```

### `scenes`

Owns:

- scene classes
- scene registry implementation
- scene bootstrap helpers
- debug overlay scene

### `systems`

Owns:

- built-in systems
- gameplay system bundles
- reusable scene-side processing logic

### `ui`

Owns:

- menus
- forms
- reusable widgets
- presentation helpers

### `spaces`

Owns:

- math
- geometry
- collision
- physics
- shared world-space primitives

These are implementation concerns and should live with the rest of the
implementation package rather than in a contracts-only package.

## Boundaries between engine domains

### Commands vs common

- `commands` orchestrate user intent
- `common` provides reusable application logic
- commands must not be the only place reusable logic exists

### Common vs engine

- `common` knows about workspaces, files, settings, and process launching
- `engine` knows about runtime behavior, frame execution, rendering, capture,
  and scenes
- `common` must not own gameplay or render-loop behavior

### Engine vs scenes/systems

- `engine` owns the shell and execution model
- `scenes` own world orchestration
- `systems` own simulation and rendering behaviors inside scenes

### Scenes/systems vs UI

- `scenes` and `systems` own simulation state and behavior
- `ui` owns reusable widgets and interaction components
- UI helpers should not own scene lifecycle logic

### Spaces vs systems

- `spaces` provides pure primitives and algorithms
- `systems` apply those primitives to live gameplay/runtime contexts

### `mini_arcade` vs `mini_arcade_core`

- `mini_arcade` owns behavior
- `mini_arcade_core` owns contracts
- if a module contains significant logic, it belongs in `mini_arcade`
- if a module defines interfaces, types, or stable schemas, it belongs in
  `mini_arcade_core`

### Backends vs runtime

- backend packages implement backend contracts only
- they should not know about commands, scaffolding, workspace layout, or game
  discovery

## What should remain in `mini_arcade_core`

Examples of good residents:

- backend port interfaces
- audio/render/input/window/capture protocols
- typed config models
- immutable runtime data structures such as `InputFrame`
- key enums and backend-neutral input types
- shared event contracts
- manifests and transport-safe value objects

Examples of code that should move out:

- engine runner implementation
- game lifecycle orchestration
- render pipeline implementation
- scene registry implementation
- built-in scene systems
- menu/forms implementation
- capture orchestration logic
- runtime service implementations

## Proposed production-ready structure

```text
packages/
  mini-arcade/
    src/mini_arcade/
      cli/
      commands/
        game/
        eg/
        system_lab/
      common/
        workspace/
        projects/
        settings/
        imports/
        process/
        scaffold/
        files/
      engine/
        lifecycle/
        loop/
        render/
        capture/
        input/
        audio/
        scene_runtime/
      scenes/
      systems/
      ui/
      spaces/
      backends/
      utils/

  mini-arcade-core/
    src/mini_arcade_core/
      contracts/
        backend/
        runtime/
        render/
        input/
        audio/
        window/
        capture/
        scene/
      models/
      events/
      types/
```

## Migration direction

### Phase 1

- finish command-domain consolidation
- keep moving shared command logic into `common`
- introduce `eg` as a dedicated command domain

### Phase 2

- move implementation-heavy runtime code out of `mini_arcade_core`
- create `mini_arcade.engine`, `mini_arcade.scenes`, `mini_arcade.systems`,
  `mini_arcade.ui`, and `mini_arcade.spaces` as the destination domains

### Phase 3

- reduce `mini_arcade_core` to protocol and model modules
- leave compatibility shims during migration
- remove old implementation paths after callers are moved

## Decision summary

The target architecture is:

- fewer top-level command domains
- clearer application vs contracts split
- reusable logic centralized in `common`
- implementation logic centralized in `mini_arcade`
- `mini_arcade_core` reserved for stable contracts only

This is the target production-ready structure for Sable at the package and
module level.
