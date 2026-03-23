# Combat and Power-Up Internals

## Purpose

This page documents the reusable combat helpers added for physics-driven arena
simulations such as `Ball vs Ball`.

The initial target is not a character-action game with steering AI. The
systems are meant for:

- bouncing fighters with health pools
- pickup-driven temporary power-ups
- projectile attacks
- collision-triggered damage
- future tournament integrations driven by the knockout bracket helpers

## Core building blocks

Implementation:
`packages/mini-arcade-core/src/mini_arcade_core/scenes/systems/builtins/combat.py`

Main types:

- `HealthPool`
  mutable hit-point state for one fighter-like entity
- `BoundsBounceBinding`
  declarative arena/bounds bounce rule for arbitrary sub-rects
- `ContactDamageBinding`
  declarative attacker/target damage rule for overlapping entities
- `ProjectileHitBinding`
  declarative projectile-vs-target hit rule

Main helpers:

- `heal_health_pool(...)`
- `damage_health_pool(...)`
- `mark_entity_dead(...)`
- `reflect_from_bounds(...)`

Main systems:

- `BoundsBounceSystem`
- `ContactDamageSystem`
- `ProjectileHitSystem`

## Design intent

These helpers deliberately stay small and composable.

They do not assume:

- one specific game genre
- one specific entity type
- one specific render style
- one specific power-up catalog

That makes them reusable for:

- two-ball arena simulations
- projectile-heavy arcade scenes
- pickup-driven prototype fights
- future original games built on the same combat primitives

## How Ball vs Ball uses them

Reference experiment:
`experiments/ball_vs_ball_combat/system_lab_case.py`

The lab combines the reusable combat helpers with existing built-ins:

- `BoundsBounceSystem`
- `KinematicMotionSystem`
- `BounceCollisionSystem`
- `PickupCollisionSystem`
- `ProjectileLifecycleBundle`
- `ProceduralParticleBundle`

The current power-up set in the lab is:

- `cure`
  heals the collector and spawns a potion-style particle burst
- `weapon`
  grants a short ranged attack and fires 3 projectiles over time
- `saw`
  boosts collision damage while active
- `shield`
  reduces incoming damage for a short duration
- `freeze`
  lets contact hits and weapon shots apply a chill debuff
- `mine`
  enables a short minefield phase that drops damaging hazards behind the
  fighter while it keeps bouncing
- `split`
  turns weapon shots into a short spread pattern
- `poison`
  lets hits apply a damage-over-time debuff

## Recommended entity shape

For fighter-like entities, the current recommended runtime fields are:

- `combat_health`
- `base_contact_damage`
- `projectile_damage`
- `saw_timer`
- `weapon_timer`
- `weapon_shots_remaining`
- `weapon_shot_cooldown`

This keeps the system generic while still being very easy to bootstrap from a
scene or lab.

## Next expansion points

The current systems are intentionally enough for a strong first combat slice.
Natural follow-ups include:

- burn status effects
- projectile variants such as homing or ricochet shot
- combat profiles that modify damage, healing, and pickup weighting without
  introducing steering AI
