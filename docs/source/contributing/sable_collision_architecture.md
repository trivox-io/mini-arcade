# Sable collision architecture

This document defines the target ownership and refactor direction for collision
handling in Sable.

The focus is not only collision detection. It is the entire collision flow:

- collider definition
- broad phase
- narrow phase
- filtering
- resolution
- gameplay consequences

The goal is to make ownership explicit so collision behavior is not spread
arbitrarily across math helpers, scene systems, and gameplay code.

## Outcome summary

The chosen direction is:

- pure collision math belongs in `spaces`
- collision orchestration belongs in `systems`
- gameplay consequences consume collision results instead of reimplementing
  collision logic
- `engine` owns scheduling only, not collision policy

This gives one clear separation:

- `spaces` answers whether and how things touch
- `systems` decide which pairs to test and what to do with the results

## Current structure

The current collision-related code is primarily spread across:

- `mini_arcade_core.spaces.collision`
- `mini_arcade_core.spaces.d2`
- `mini_arcade_core.spaces.physics`
- `mini_arcade_core.scenes.systems.builtins.combat`
- `mini_arcade_core.scenes.systems.builtins.movement`
- several gameplay-specific built-in systems

That means collision logic is currently split between:

- pure overlap helpers
- older OOP collider wrappers
- gameplay systems doing detection and consequence together
- movement and bounce helpers acting as partial resolution logic

## Collision ownership

## `spaces.collision`

Owner responsibility:

- collider specs
- shape-pair intersection algorithms
- narrow-phase collision checks
- contact and manifold result types
- pure collision queries

This domain should answer:

- do these shapes overlap
- where do they touch
- along what normal
- by how much

This domain should not answer:

- whether the pair should be tested
- whether the entities are allowed to interact
- how gameplay should respond

## `spaces.physics`

Owner responsibility:

- generic physical response helpers
- reflection math
- separation math
- impulse-like helpers
- positional correction helpers

This domain should answer:

- how to separate overlapping shapes
- how to reflect or redirect velocity
- how to apply generic physical response

This domain should not answer:

- whether damage is applied
- whether a pickup is consumed
- whether a projectile dies

## `systems.collision`

Owner responsibility:

- broad phase candidate generation
- collision filtering
- orchestration of narrow-phase checks
- dispatch of resolution or gameplay callbacks
- collision events and collision policies

This domain should answer:

- which entity pairs are worth checking
- which pairs are allowed to interact
- which narrow-phase test to run
- whether the result goes to physical resolution, gameplay consequence, or both

This domain should not own:

- low-level overlap math
- generic vector/geometry calculations better owned by `spaces`

## Gameplay systems

Owner responsibility:

- damage
- pickup collection
- projectile hit consequences
- triggers
- hazards
- score and chain effects

Gameplay systems should consume collision results.

They should not own:

- broad phase
- shape intersection math
- generic separation or bounce resolution

## `engine`

Owner responsibility:

- schedule when collision systems run during the frame

The engine should not own:

- collision rules
- filter policy
- shape tests
- gameplay consequences

## Current structural problems

## 1. Collision primitives are split across two spatial domains

Current overlap:

- `spaces.collision`
- `spaces.d2.collision2d`

Problem:

- both represent collision logic
- one is function/spec-based
- one is older object-style wrapper logic
- long-term ownership is unclear

Impact:

- developers cannot tell which API is the real one
- migration tends to create more duplicate collision code

## 2. Broad phase does not exist as a first-class domain

Current state:

- systems typically iterate all candidate entities directly
- pair generation is embedded inside gameplay systems

Problem:

- candidate generation is duplicated
- there is no shared scaling path
- collision pipelines are difficult to reason about

Impact:

- each system implements its own local pair loop
- performance and behavior differ from one gameplay layer to another

## 3. Narrow phase is underspecified

Current state:

- `intersections.py` is mainly boolean rect overlap
- entity intersection is often reduced to `intersects_entities(...)`

Problem:

- boolean-only overlap is too weak for general collision architecture
- contact normal, penetration depth, and manifold data are not first-class

Impact:

- systems that need resolution must recompute or invent their own response
- the codebase mixes “detection” and “resolution assumptions”

## 4. Filtering is ad hoc

Current state:

- predicates exist inside systems such as combat/projectile rules
- there is no shared filter model

Problem:

- filtering policy is hidden in local lambdas and per-system logic
- layer/mask/group ownership is undefined

Impact:

- collision semantics are hard to inspect globally
- similar systems express filtering differently

## 5. Resolution is mixed into gameplay systems

Current state:

- bounce logic appears in movement/combat helpers
- physical response is tied to gameplay systems

Problem:

- “collision happened” and “what the game does next” are tightly coupled

Impact:

- reuse is reduced
- generic physics response cannot evolve independently

## 6. Detection and consequence are coupled

Current state:

- projectile hits, contact damage, and pickup collection each do their own
  pair iteration and overlap handling

Problem:

- the same flow is repeated with different consequences

Impact:

- duplicated logic
- inconsistent collision behavior across gameplay domains

## Desired collision flow

The target collision flow is:

1. Collider authoring
2. Broad phase
3. Filtering
4. Narrow phase
5. Resolution
6. Gameplay consequence

### 1. Collider authoring

Entities expose collision data using explicit collider specs.

That data should define:

- shape
- size
- optional offsets
- optional collision category metadata

### 2. Broad phase

Generate possible pairs cheaply.

Examples:

- all-pairs for tiny worlds
- bucket grid / spatial hash for larger worlds
- specialized single-vs-many scans for projectiles and hazards

Output:

- candidate pairs only

### 3. Filtering

Decide which candidate pairs are allowed to interact.

Examples:

- ignore same-owner projectile pairs
- ignore dead or inactive entities
- ignore pairs blocked by tags, groups, or categories
- ignore entities outside active simulation rules

Output:

- filtered candidate pairs

### 4. Narrow phase

Run exact collision checks using the appropriate shape pair algorithm.

Output should be more than `bool` when needed.

Preferred result:

- contact/manifold object containing:
  - overlap flag
  - contact normal
  - penetration depth
  - optional contact point(s)

### 5. Resolution

Apply generic physical resolution when the interaction requires it.

Examples:

- separation
- bounce/reflection
- velocity adjustment
- positional correction

This stage should stay generic and reusable.

### 6. Gameplay consequence

Apply game-specific meaning.

Examples:

- deal damage
- collect pickup
- destroy projectile
- trigger explosion
- increment score chain

This stage should consume collision outputs rather than recalculate them.

## Proposed ownership model

## Layer 1: pure collision and physics primitives

Owned by:

- `spaces.collision`
- `spaces.physics`

Responsibilities:

- collider definitions
- shape intersection
- contact generation
- physical response math

No scene context.
No world queries.
No gameplay side effects.

## Layer 2: collision pipeline

Owned by:

- `systems.collision`

Responsibilities:

- broad phase
- filtering
- narrow-phase orchestration
- optional routing to physics resolution
- collision event production

Scene-aware, but still generic.

## Layer 3: gameplay consequences

Owned by:

- gameplay systems in `systems`

Responsibilities:

- use collision results to drive damage, pickups, hazards, scoring, etc.

These systems should not decide how overlap math works.

## Chosen refactor direction

The chosen direction is:

- keep `spaces.collision` as the long-term home for collision primitives
- keep `spaces.physics` as the long-term home for generic response math
- introduce an explicit collision pipeline domain on the `systems` side
- phase out or absorb duplicate collision logic in `spaces.d2`
- move gameplay-specific collision flow out of generic helper modules where it
  currently mixes detection and consequence

This is the selected direction because it creates the clearest split between:

- pure math
- pipeline orchestration
- gameplay meaning

## Proposed target module shape

```text
spaces/
  collision/
    specs.py
    shapes.py
    manifolds.py
    narrow_phase.py
    queries.py
  physics/
    response.py
    separation.py

systems/
  collision/
    broad_phase.py
    filters.py
    pipeline.py
    events.py
    resolvers.py
```

The exact filenames can change, but the ownership split should remain.

## High-risk boundary problems

## 1. `intersects_entities(...)` is too convenient

Risk:

- it hides collider assumptions
- it encourages boolean-only collision flows

Why it matters:

- callers stop distinguishing between broad phase, narrow phase, and resolution

## 2. `None` collider fallback semantics are ambiguous

Risk:

- “missing collider means rect from transform” creates invisible policy

Why it matters:

- the collision system becomes harder to reason about and document

## 3. `spaces.d2` competes with `spaces.collision`

Risk:

- duplicate APIs remain live
- future work may use the wrong layer

Why it matters:

- migration will keep stalling if both are treated as valid long-term homes

## 4. Bounce logic is spread across unrelated modules

Risk:

- bounds bounce and contact bounce evolve differently
- physical response remains inconsistent

Why it matters:

- resolution should be generic, not scattered

## 5. Gameplay systems currently own too much of the collision pipeline

Risk:

- projectile, pickup, contact, and hazard systems repeat candidate generation
  and filtering logic

Why it matters:

- every gameplay domain becomes its own collision stack

## 6. Performance scaling has no shared path

Risk:

- broad-phase optimization becomes harder later
- performance work requires changing many systems independently

Why it matters:

- collision architecture should scale structurally, not only by local patching

## Refactor plan

The chosen execution plan is:

### Phase 1: document and freeze ownership

- document current problems
- document desired flow
- document target ownership

### Phase 2: create explicit collision pipeline contracts

- define contact/manifold result type
- define filter model
- define pair pipeline interfaces

### Phase 3: introduce `systems.collision`

- add broad phase
- add filtering
- add narrow-phase orchestration

### Phase 4: migrate one vertical slice first

Recommended first slice:

- projectile or contact overlap systems

Reason:

- simpler than full bounce resolution
- proves the new flow end to end

### Phase 5: migrate generic resolution helpers

- separate response math from gameplay systems
- move bounce/separation helpers into physics-owned modules

### Phase 6: retire duplicate collision paths

- absorb or remove `spaces.d2.collision2d`
- deprecate convenience APIs that hide ownership

## Decision summary

Collision ownership for Sable is:

- `spaces.collision`: narrow-phase primitives
- `spaces.physics`: generic physical response
- `systems.collision`: broad phase, filtering, orchestration
- gameplay systems: domain-specific consequences
- `engine`: scheduling only

The current architecture mixes these concerns. The chosen refactor direction is
to separate them into explicit layers so collision can scale in both clarity
and performance.
