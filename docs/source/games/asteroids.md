# Asteroids

Minimal Asteroids clone built on `mini-arcade-core` with the pygame backend.

## What it validates

- Pygame backend integration in a full game
- Scene discovery and menu/game scene transitions
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
