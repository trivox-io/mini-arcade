# Deja Bounce

A minimalist Pong-like reference game built on Mini Arcade.

## What it validates

- Scene and system pipeline organization
- Input-to-intent flow
- 2D collisions and bounce behavior
- Runtime services integration (audio, window, render)
- Capture hooks (screenshots/video/replay as configured)

## Run

From repo root:

```bash
python -m mini_arcade.main run --game deja-bounce
```

Alternative (inside `games/deja-bounce`):

```bash
python manage.py
```

## Notes

Deja Bounce is used as both a playable sample and an engine regression target.
