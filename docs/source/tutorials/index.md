# Tutorials

Tutorials map to runnable examples under `examples/catalog/`.

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

```{toctree}
:caption: Tutorials
:maxdepth: 1

config/engine_config_basics
```

```{toctree}
:hidden:
:caption: Examples Roadmap

Roadmap <roadmap>
```
