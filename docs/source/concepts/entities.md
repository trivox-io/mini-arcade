# Entities Internals

## Purpose

Explain the core entity contract used across examples and games.

## Core file

- `packages/mini-arcade-core/src/mini_arcade_core/engine/entities.py`

## Entity structure

`BaseEntity` combines:

- identity:
  `id`, `name`, `codename`, `tags`
- transform:
  position, size, rotation
- visual data:
  `shape`, `style`, `sprite`, `anim`
- simulation data:
  `kinematic`, `life`
- optional collision data:
  `collider`

## `from_dict(...)`

`BaseEntity.from_dict(...)` is the main plain-data entrypoint. It parses:

- `transform.center`
- `transform.size`
- `transform.rotation_deg`
- `shape.kind`
- `style.fill` / `style.stroke`
- `kinematic.velocity` / `kinematic.acceleration` / `kinematic.max_speed`
- `sprite.texture`
- `anim.frames` / `anim.fps` / `anim.loop`

That makes it a good fit for:

- examples
- YAML-driven scene bootstrap
- test fixtures
- runtime spawn templates

`kinematic` data by itself does not move anything. A scene system has to consume
it, either through custom gameplay code or the built-in movement systems.

`tags` are preserved and normalized as lowercase unique strings. They are the
preferred way to express gameplay-facing categories such as `ship`, `bullet`,
`alien`, or `paddle`.

## World queries and id domains

`BaseWorld` is the query surface scenes should use around entities.

Preferred query model:

- `find_entity(tag="ship")`
- `find_entities(tag="bullet")`
- scene-local helpers like `world.ship()` or `world.aliens()`

For scenes that still need constrained runtime allocation, `BaseWorld` also
supports named entity-id domains:

- `entity_id_domains = {"bullet": EntityIdDomain(...)}`
- `get_entities_in_domain("bullet")`
- `allocate_entity_id_for("bullet")`
- `compact_tracked_entity_ids_for(attr_name="bullets", domain_name="bullet")`

Practical rule:

- use `tags` and world helper methods for gameplay logic and rendering
- use named id domains only for allocation, cleanup, or compatibility with
  fixed-content layouts

## Render precedence

The built-in queued renderer uses this priority:

1. `anim.texture`
2. `sprite.texture`
3. `shape` + `style`

That is why sprite/animation examples can use the same entity transform data as
shape examples.

## Tutorial references

- `docs/source/tutorials/entity/base_entity_from_dict.md`
- `docs/source/tutorials/entity/sprite_texture_basics.md`
- `docs/source/tutorials/entity/animation_frames_basics.md`
