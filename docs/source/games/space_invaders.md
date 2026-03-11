# Space Invaders

Space Invaders clone used as a Mini Arcade reference game.

## What it validates

- Sprite-based rendering
- Projectile/cooldown gameplay loops
- Multi-entity update systems
- Declarative gameplay shell plus feature-specific processors
- Tags and named id domains for large-scene entity management
- Scene transitions and command flow
- Asset loading patterns in a larger game module

## Run

From repo root:

```bash
python -m mini_arcade.main run --game space-invaders
```

Alternative (inside `games/space-invaders`):

```bash
python manage.py
```

## Notes

This game intentionally keeps mechanics readable so engine behavior is easy to
inspect and debug.

## Implementation map

- Bootstrap:
  - `games/space-invaders/manage.py`
  - `games/space-invaders/src/space_invaders/app.py`
- Settings profile:
  - `games/space-invaders/settings/settings.yml`
- Scene package:
  - `games/space-invaders/src/space_invaders/scenes/`
- Good files to study:
  - `games/space-invaders/src/space_invaders/scenes/space_invaders/scene.py`
  - `games/space-invaders/src/space_invaders/scenes/space_invaders/models.py`
  - `games/space-invaders/src/space_invaders/scenes/space_invaders/systems/__init__.py`
