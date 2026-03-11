# Deja Bounce

A minimalist Pong-like reference game built on Mini Arcade.

## What it validates

- Declarative `GameScene` shell wiring
- System bundles for movement/composite features
- Input-to-intent flow from settings-driven bindings
- Extracted world builder and pipeline builder around a small gameplay scene
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

## Implementation map

- Bootstrap:
  - `games/deja-bounce/manage.py`
  - `games/deja-bounce/src/deja_bounce/app.py`
- Settings profile:
  - `games/deja-bounce/settings/settings.yml`
- Scene package:
  - `games/deja-bounce/src/deja_bounce/scenes/`
- Good files to study:
  - `games/deja-bounce/src/deja_bounce/scenes/pong/scene.py`
  - `games/deja-bounce/src/deja_bounce/scenes/pong/bootstrap.py`
  - `games/deja-bounce/src/deja_bounce/scenes/pong/pipeline.py`
  - `games/deja-bounce/src/deja_bounce/scenes/pong/models.py`
  - `games/deja-bounce/src/deja_bounce/scenes/pong/systems/__init__.py`
