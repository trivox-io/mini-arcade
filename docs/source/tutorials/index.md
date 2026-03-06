# Tutorials

Tutorials map to runnable examples under `examples/catalog/`.

If your goal is to build a new game package end-to-end, start here:

- [Create a Game](create_game.md)

## Before You Start: Game Structure

Use this baseline layout for CLI-runnable games:

```text
games/<game-id>/
  pyproject.toml
  manage.py
  settings/
    settings.yml
  src/<python_package>/
    __main__.py
    app.py
    constants.py
    difficulty.py
    scenes/
      __init__.py
      commands.py
      menu.py
      pause.py
      gameplay/
        scene.py
        models.py
        entities.py
        systems/
          input.py
          rules.py
          render.py
    entities/
      __init__.py
      paddle.py
      ball.py
    controllers/
      __init__.py
      cpu.py
  assets/
    fonts/
    sfx/
  tests/
```

### Scene File Responsibilities

Recommended separation per scene/module:

- `scenes/menu.py`:
  main menu UI scene (start game, settings, quit, difficulty cycling). It
  should mainly orchestrate navigation commands, not gameplay simulation.
- `scenes/pause.py`:
  pause overlay scene (continue, restart, return to menu). Keep it focused on
  pausing flow and user decisions.
- `scenes/gameplay/scene.py`:
  core gameplay scene. Register scene id, initialize world, wire systems, and
  define the tick/update pipeline.
- `scenes/gameplay/models.py`:
  dataclasses for world state and tick context used by the gameplay scene and
  systems.
- `scenes/gameplay/entities.py`:
  gameplay-specific entity assembly/helpers (spawn/build helpers). If entities
  are shared across scenes, move concrete classes to top-level `entities/`.
- `scenes/gameplay/systems/input.py`:
  translate input frames into intents/actions.
- `scenes/gameplay/systems/rules.py`:
  collision/scoring/win-lose rules and other game mechanics.
- `scenes/gameplay/systems/render.py`:
  convert world state into render operations.
- `scenes/commands.py`:
  command objects for scene transitions and game actions used across scenes.

Required `pyproject.toml` metadata:

```toml
[tool.mini-arcade.game]
id = "<game-id>"
entrypoint = "manage.py"
source_roots = ["src"]
```

This metadata is how `mini-arcade run --game <game-id>` discovers and launches
your game. For a concrete, complete reference, see
`games/deja-bounce/` and the tutorial `config/engine_config_basics`.

## Game Settings YAML (`settings/settings.yml`)

Each game should include a local profile at:

```text
games/<game-id>/settings/settings.yml
```

The loader call:

```python
settings = Settings.for_game("<game-id>", required=True)
```

looks for that file and exposes normalized sections through:

- `settings.scene_defaults()`
- `settings.engine_config_defaults()`
- `settings.backend_defaults()`
- `settings.gameplay_defaults()`

Recommended baseline template:

```yaml
game:
  id: <game-id>

project:
  # Optional. Defaults to games/<game-id> when omitted.
  root: ${settings_dir}/..
  # Optional. Defaults to ${project_root}/assets when omitted.
  assets_root: ${project_root}/assets

scene:
  initial_scene: menu
  scene_registry:
    discover_packages:
      - <python_package>.scenes

engine_config:
  fps: 60
  virtual_resolution: [800, 600]
  enable_profiler: false
  postfx:
    enabled: false
    active: []

backend:
  provider: native # or pygame
  window:
    width: 800
    height: 600
    title: <Game Title>
    resizable: true
  renderer:
    background_color: [20, 20, 20]
  fonts:
    - name: default
      path: ${assets_root}/fonts/<font-file>.ttf
      size: 24
  audio:
    enable: true
    sounds:
      ui_select: sfx/ui_select.wav

gameplay:
  difficulty:
    default: normal
```

Notes:

- `scene.initial_scene` and `scene.scene_registry.discover_packages` map to
  `SceneConfig`.
- `engine_config.*` maps to `EngineConfig` (`fps`, `virtual_resolution`,
  `postfx`, `enable_profiler`).
- Relative asset/audio/font paths are resolved from `assets_root`.
- Available path tokens include:
  `${settings_dir}`, `${project_root}`, `${assets_root}`, `${repo_root}`, and
  `${cwd}`.
- Keep game-specific runtime settings with the game itself; use repo-level
  `settings/settings.yml` only for shared defaults.

```{toctree}
:caption: Tutorials
:maxdepth: 1

create_game
config/engine_config_basics
config/backend_swap
```

```{toctree}
:hidden:
:caption: Examples Roadmap

Roadmap <roadmap>
```
