# config/engine_config_basics

## Goal

Learn the current config model (`EngineConfig` + `SceneConfig`) and how one
example can switch backends and runtime parameters without changing scene code.

For a full end-to-end game creation workflow, see [../create_game.md](../create_game.md).

## What this example demonstrates

This example connects four pieces:

1. Settings profile:
   `examples/settings/config/engine_config_basics.yml`
2. Example builder:
   `examples/catalog/config/engine_config_basics/main.py`
3. Shared runner:
   `examples/_shared/runner.py`
4. Runtime scene:
   `examples/catalog/config/engine_config_basics/scenes/scene.py`

Execution flow:

1. `build_example()` loads defaults from the settings profile.
2. CLI passthrough args override those defaults (`--backend`, `--fps`, etc.).
3. The runner creates:
   - `EngineConfig` from engine values (`fps`, `virtual_resolution`, `postfx`)
   - `SceneConfig` from scene values (`initial_scene`, `discover_packages`)
4. The scene renders the effective config so you can verify what is active.

## Run

Default:

```bash
mini-arcade run --example config/engine_config_basics
```

Swap backend:

```bash
mini-arcade run --example config/engine_config_basics --pass-through --backend pygame
mini-arcade run --example config/engine_config_basics --pass-through --backend native
```

Override engine parameters:

```bash
mini-arcade run --example config/engine_config_basics --pass-through --fps 72 --virtual-width 960 --virtual-height 540
```

Enable profiler + postfx:

```bash
mini-arcade run --example config/engine_config_basics --pass-through --enable-profiler --postfx-enabled --postfx-active crt,vignette_noise
```

## Tutorial intro: game folder structure (Deja Bounce reference)

Use this as a baseline structure for new games:

```text
games/deja-bounce/
  pyproject.toml
  manage.py
  settings/
    settings.yml
  src/deja_bounce/
    __main__.py
    app.py
    constants.py
    difficulty.py
    scenes/
      commands.py
      menu.py
      pause.py
      pong/
        scene.py
        models.py
        draw_ops.py
        systems/
          input.py
          pause.py
          render.py
    entities/
    controllers/
  assets/
    fonts/
    sfx/
  tests/
```

What each part should contain:

- `pyproject.toml`: package metadata + CLI discovery metadata.
- `manage.py`: simple launcher script for local execution.
- `settings/settings.yml`: game-local runtime defaults loaded by
  `Settings.for_game("<game-id>")`.
- `src/<game_id>/app.py`: bootstrap (`Settings`, backend loader, `run_game`).
- `src/<game_id>/scenes/`: scene classes registered via `@register_scene(...)`.
- `src/<game_id>/scenes/commands.py`: scene/gameplay commands.
- `src/<game_id>/entities/`: domain entities and value objects.
- `src/<game_id>/controllers/`: AI/input helpers and control logic.
- `assets/`: fonts, sounds, sprites, music, etc.
- `tests/`: unit/integration tests.
- `games/<game-id>/settings/settings.yml`: game-local runtime settings file
  consumed by `Settings.for_game("<game-id>")`.

## Game settings file example (`games/<game-id>/settings/settings.yml`)

Minimal starter config:

```yaml
scene:
  initial_scene: menu
  scene_registry:
    discover_packages:
      - deja_bounce.scenes

engine_config:
  fps: 60
  virtual_resolution: [800, 600]
  enable_profiler: false
  postfx:
    enabled: false
    active: []

backend:
  provider: native
  window:
    width: 800
    height: 600
    title: Deja Bounce
```

This is read by `Settings.for_game("deja-bounce")` and transformed into:

- `SceneConfig` via `settings.scene_defaults()`
- `EngineConfig` via `settings.engine_config_defaults()`
- backend defaults via `settings.backend_defaults()`

## Required `pyproject.toml` section for CLI game discovery

To run a game with:

```bash
mini-arcade run --game <game-id>
```

you need this section in `games/<game-id>/pyproject.toml`:

```toml
[tool.mini-arcade.game]
id = "deja-bounce"
entrypoint = "manage.py"
source_roots = ["src"]
```

Field meaning:

- `id`: CLI game id (`--game deja-bounce`).
- `entrypoint`: script path executed by the runner.
- `source_roots`: roots added to `PYTHONPATH` when launching.

## Concepts covered

- Split config responsibilities:
  - `EngineConfig`: fps, virtual resolution, postfx, profiler.
  - `SceneConfig`: initial scene + scene discovery packages.
- Settings profile defaults with CLI overrides.
- Backend switching (`pygame` / `native`) without scene code changes.
- Virtual resolution vs window size.

## Controls

- `F1`: toggle built-in debug overlay
- `ESC`: exit

## Next step

- Continue with `config/backend_swap` to validate parity between backends.
- Use [Create a Game](../create_game.md) to scaffold a full game package.
