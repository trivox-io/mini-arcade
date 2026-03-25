# Sable module ownership

This document defines ownership at the module and domain level for Sable.

The purpose is to stop rendering, collision, scenes, backend integration,
systems, and shared utilities from overlapping without a clear home.

It complements the target package-structure document by answering a different
question:

- package structure answers where code should live
- module ownership answers what each domain is allowed to own

## Outcome summary

The target ownership model is:

- each domain has one primary responsibility
- cross-domain dependencies are directional, not circular
- overlap points are explicitly identified
- high-risk boundaries are called out so they can be migrated deliberately

## Ownership model

## `backend`

Owns:

- backend-neutral backend contracts
- backend-facing types, keys, events, viewport primitives, and adapter utilities
- implementation of provider-specific rendering, audio, input, window, and
  capture plumbing in backend packages

Does not own:

- scene logic
- gameplay logic
- command behavior
- workspace or project discovery

Boundary rule:

- backends implement platform capability
- they do not define engine policy

## `engine`

Owns:

- game lifecycle
- manager composition
- main loop orchestration
- command queue execution
- render pipeline orchestration
- frame timing and loop hooks
- capture orchestration at the runtime level

Does not own:

- game-specific simulation rules
- scene-local gameplay decisions
- reusable CLI or workspace logic

Boundary rule:

- `engine` runs the shell
- it does not decide gameplay behavior

## `runtime`

Owns:

- runtime service interfaces and adapters
- audio, input, capture, file, window, render, and scene-query service surfaces
- runtime context aggregation
- transport-safe runtime data like `InputFrame`

Does not own:

- engine loop policy
- scene lifecycle policy
- backend-specific platform logic
- gameplay systems

Boundary rule:

- `runtime` exposes service surfaces
- `engine` consumes them

## `engine.render`

Owns:

- render pipeline structure
- render context
- frame packet flow
- camera and viewport composition policy
- render-service interaction

Does not own:

- UI widget behavior
- backend texture implementation
- game-specific draw rules

Boundary rule:

- render orchestration belongs here
- draw content decisions belong to scenes and systems

## `runtime.render`

Owns:

- render port contracts only

Does not own:

- render pipeline implementation
- frame composition logic

Boundary rule:

- `runtime.render` is a contract surface
- `engine.render` is an implementation domain

## `scenes`

Owns:

- scene classes
- scene registry and discovery
- scene bootstrap helpers
- scene-local world construction
- debug overlay and other reusable scene shells

Does not own:

- low-level math/collision primitives
- backend/platform concerns
- generic filesystem/process helpers

Boundary rule:

- scenes orchestrate world state and installed systems
- they should not absorb platform or repository concerns

## `systems`

Owns:

- reusable simulation processors
- scene-installed behavior bundles
- gameplay update rules
- render-emission logic owned by systems
- built-in gameplay layers such as movement, projectiles, particles, brackets,
  combat, and mode-specific rules

Does not own:

- engine lifecycle
- backend/platform integration
- repo/workspace logic

Boundary rule:

- systems transform scene state
- they should not own global application policy

## `spaces`

Owns:

- math primitives
- geometry primitives
- collision primitives
- physics primitives
- pure spatial algorithms

Does not own:

- scene entities with gameplay semantics
- render policy
- engine loop behavior
- command/runtime services

Boundary rule:

- `spaces` must stay pure and reusable
- if logic needs scene context, it belongs in `systems`

## `ui`

Owns:

- menus
- forms
- widgets
- reusable visual interaction helpers

Does not own:

- scene lifecycle
- render pipeline
- filesystem/process logic
- backend contracts

Boundary rule:

- `ui` defines reusable interaction components
- scenes decide where and how to use them

## `common`

Owns:

- reusable application logic outside the runtime engine
- workspace discovery
- project metadata loading
- settings helpers
- import/path helpers
- subprocess helpers
- scaffold helpers
- file and repo utilities

Does not own:

- scene/gameplay logic
- render pipeline logic
- backend integration

Boundary rule:

- `common` is application support code
- it is not an engine domain

## `utils`

Owns:

- low-level generic helpers with no better domain home

Does not own:

- domain policy
- code that has a clear engine, runtime, scene, system, UI, or common home

Boundary rule:

- `utils` should remain small
- any helper with domain knowledge should move to its owning domain

## Current overlap and ambiguity

The current codebase has several places where ownership is blurred.

### Rendering overlap

Current overlap:

- `backend`
- `runtime.render`
- `engine.render`
- scene/system render helpers
- `ui`

Why this is ambiguous:

- the contract surface, orchestration layer, and render content layer all exist
  together, but their responsibilities are not sharply separated

Target resolution:

- `backend`: provider implementation only
- `runtime.render`: render port contract only
- `engine.render`: pipeline orchestration only
- `scenes` / `systems`: render content emission
- `ui`: reusable widgets and input/presentation helpers

### Collision overlap

Current overlap:

- `spaces.collision`
- `spaces.d2`
- `scenes.systems.builtins`

Why this is ambiguous:

- there are multiple collision-related homes, including both pure primitives and
  scene-aware collision behavior

Target resolution:

- `spaces.collision` and `spaces.physics`: pure primitives only
- scene-aware collision response belongs in `systems`
- the `d2` layer should either be absorbed into the pure spatial layer or
  retired if it duplicates `geometry`, `collision`, and `physics`

### Scenes vs engine scenes

Current overlap:

- `engine.scenes`
- `scenes`
- `runtime.scene`

Why this is ambiguous:

- scene management, scene contracts, and scene classes are split across three
  different areas

Target resolution:

- scene runtime orchestration belongs to `engine`
- scene query contracts belong to `runtime.scene`
- scene classes and registration belong to `scenes`

### Systems vs scenes

Current overlap:

- `game_scene.py`
- `sim_scene.py`
- `scenes.systems.builtins`

Why this is ambiguous:

- some gameplay behavior lives in scene shells, some in built-in systems, and
  some in scene-specific helpers

Target resolution:

- scenes orchestrate
- systems implement behavior
- scene shells should stay declarative and thin

### Backend integration overlap

Current overlap:

- `backend`
- `runtime.*_adapter`
- `engine.game`

Why this is ambiguous:

- adapter wiring and backend ownership are spread across several levels

Target resolution:

- backend packages implement platform behavior
- runtime adapters expose stable ports
- engine composes those ports

### Shared utilities overlap

Current overlap:

- `utils`
- `common`
- ad hoc helpers inside engine and scene modules

Why this is ambiguous:

- “utility” behavior risks becoming a dumping ground when ownership is unclear

Target resolution:

- if a helper knows about workspaces or commands, it belongs in `common`
- if it knows about rendering, scenes, systems, or runtime, it belongs in that
  domain
- `utils` should be reserved for truly generic helpers

## Proposed ownership statements by domain

### Rendering

Owner:

- `engine.render` for orchestration
- `runtime.render` for contracts
- `backend` packages for provider implementation
- `systems` and `scenes` for render content

### Collision

Owner:

- `spaces.collision` and `spaces.physics` for primitives
- `systems` for gameplay collision responses

### Scenes

Owner:

- `scenes` for scene definitions, scene registration, and scene bootstrap
- `engine` for scene stack execution

### Backend integration

Owner:

- backend packages implement platform behavior
- `runtime` defines service ports and adapters
- `engine` performs composition

### Systems

Owner:

- `systems` owns reusable simulation and render-emission behaviors

### Shared utilities

Owner:

- `common` owns shared application support logic
- `utils` owns only domain-neutral helpers

## High-risk boundary problems

These are the main boundary problems that create migration risk.

### 1. `mini_arcade_core` mixes contracts and implementation

Risk:

- migration becomes piecemeal and confusing
- package role remains ambiguous

Why it matters:

- the package cannot be both “contracts-only” and the home of engine logic

### 2. Rendering is split across too many layers

Risk:

- render bugs are harder to place
- ownership between backend, runtime, engine, UI, and systems becomes unclear

Why it matters:

- rendering is one of the most central cross-cutting concerns in the engine

### 3. Collision logic is duplicated between pure and scene-aware layers

Risk:

- inconsistent collision behavior
- duplicated math and policy
- unclear migration path for gameplay systems

### 4. Scene runtime concerns are divided across `engine`, `runtime.scene`,
`engine.scenes`, and `scenes`

Risk:

- scene ownership remains muddy
- future refactors can move code in the wrong direction

### 5. Built-in systems in `mini_arcade_core` are effectively implementation
domains

Risk:

- large portions of gameplay logic remain trapped in the contracts package
- migration later becomes broader and more disruptive

### 6. `utils` can become a sink for unresolved ownership

Risk:

- architecture becomes harder to reason about
- code keeps being added without proper domain placement

## Rules for future placement

Use these rules when deciding module ownership.

- If code is a protocol, schema, event, or stable type, it belongs in
  `mini_arcade_core`
- If code contains behavior, it belongs in `mini_arcade`
- If code knows about workspaces, settings files, scaffolding, or subprocesses,
  it belongs in `common`
- If code knows about frame execution, scene stack handling, or rendering
  orchestration, it belongs in `engine`
- If code knows about gameplay state transformation, it belongs in `systems`
- If code is pure math/geometry/collision/physics, it belongs in `spaces`
- If code is a widget or reusable interaction component, it belongs in `ui`
- If code has no domain knowledge at all, it may belong in `utils`

## Decision summary

The ownership model for Sable is:

- `backend`: platform implementation
- `runtime`: service ports and adapters
- `engine`: lifecycle and orchestration
- `engine.render`: render orchestration
- `scenes`: scene definitions and registration
- `systems`: gameplay and render-emission behavior
- `spaces`: pure spatial primitives
- `ui`: reusable interaction widgets
- `common`: reusable application support logic
- `utils`: minimal domain-neutral helpers

The major architecture problem today is not only package placement. It is
ownership ambiguity between these domains. The target state is a system where
each domain has one primary job and overlap is treated as a migration problem,
not as an acceptable steady state.
