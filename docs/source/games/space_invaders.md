# Space Invaders

Space Invaders clone used as a Mini Arcade reference game.

## What it validates

- Sprite-based rendering
- Projectile/cooldown gameplay loops
- Multi-entity update systems
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
