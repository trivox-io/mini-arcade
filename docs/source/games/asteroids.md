# Asteroids

Minimal Asteroids clone built on `mini-arcade-core` with the pygame backend.

## What it validates

- Pygame backend integration in a full game
- Scene discovery and menu/game scene transitions
- Shape-heavy rendering with declarative queued render composition
- System bundles plus bounded spawn-id domains
- Ship movement, projectiles, and arcade-style loop structure

## Run

From repo root:

```bash
python -m mini_arcade.main run --game asteroids
```

Alternative (inside `games/asteroids`):

```bash
python manage.py
```

## Controls

- `Left` / `Right`: rotate ship
- `Up`: thrust
- `Space`: fire
- `Esc`: pause

## Implementation map

- Bootstrap:
  - `games/asteroids/manage.py`
  - `games/asteroids/src/asteroids/app.py`
- Settings profile:
  - `games/asteroids/settings/settings.yml`
- Scene package:
  - `games/asteroids/src/asteroids/scenes/`
- Good files to study:
  - `games/asteroids/src/asteroids/scenes/asteroids/scene.py`
  - `games/asteroids/src/asteroids/scenes/asteroids/models.py`
  - `games/asteroids/src/asteroids/scenes/asteroids/systems/__init__.py`
