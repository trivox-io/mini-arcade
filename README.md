# Mini Arcade

> A Python-first mini game engine and toolkit for building small arcade games.

[![CI](https://github.com/trivox-io/mini-arcade/actions/workflows/ci.yml/badge.svg)](https://github.com/trivox-io/mini-arcade/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/trivox-io/mini-arcade)](./LICENSE)
[![PyPI](https://img.shields.io/pypi/v/mini-arcade)](https://pypi.org/project/mini-arcade/)
[![Docs](https://img.shields.io/badge/docs-in%20repo-blue)](./docs)

Mini Arcade is a monorepo with a simulation-first engine core, swappable backends
(native SDL2 and pygame), runnable examples, and reference games.

## Status

Current status: alpha.

The project is actively developed and APIs may still evolve.

## Quick Start

Install:

```bash
pip install mini-arcade
```

Run from an installed environment:

```bash
mini-arcade run --example config/engine_config_basics
mini-arcade run --game deja-bounce
```

Equivalent module form:

```bash
python -m mini_arcade.main run --example config/engine_config_basics
python -m mini_arcade.main run --game deja-bounce
```

## Core Features

- Scene registry and scene stack with overlays
- System pipeline with ordered phases
- Command queue for scene/game actions
- Runtime services (window, input, render, audio, capture, files)
- Render pipeline passes (begin, world, lighting, ui, postfx, end)
- Built-in capture hooks (screenshot, replay, video frame capture)
- Swappable backends:
  - `mini-arcade-pygame-backend`
  - `mini-arcade-native-backend`

## CLI Usage

Run a game:

```bash
mini-arcade run --game asteroids
```

Run an example:

```bash
mini-arcade run --example config/backend_swap
```

Forward args to the example runner:

```bash
mini-arcade run --example config/backend_swap --pass-through --backend native --fps 72
```

## API Usage (Core)

```python
from mini_arcade_core import EngineConfig, SceneConfig, run_game
from mini_arcade_pygame_backend import PygameBackend, PygameBackendSettings

backend_settings = PygameBackendSettings.from_dict(
    {
        "window": {"width": 960, "height": 540, "title": "My Game"},
        "renderer": {"background_color": (20, 20, 20)},
    }
)
backend = PygameBackend(settings=backend_settings)

engine_config = EngineConfig(
    fps=60,
    virtual_resolution=(960, 540),
    enable_profiler=False,
)
scene_config = SceneConfig(
    initial_scene="menu",
    discover_packages=["my_game.scenes", "mini_arcade_core.scenes"],
)

run_game(
    engine_config=engine_config,
    scene_config=scene_config,
    backend=backend,
)
```

## Create Your Own Game

Use the detailed guide:

- [docs/source/tutorials/create_game.md](./docs/source/tutorials/create_game.md)

That guide includes:

- required folder and metadata layout
- complete `settings.yml` template
- minimal runnable scene and commands
- full bootstrap (`manage.py` + `app.py`) pattern used by current games

## Monorepo Layout

```text
mini-arcade/
|- packages/
|  |- mini-arcade/
|  |- mini-arcade-core/
|  |- mini-arcade-pygame-backend/
|  `- mini-arcade-native-backend/
|- games/
|- examples/
|- docs/
`- scripts/
```

## Documentation

- [Quickstart](./docs/source/quickstart.md)
- [Architecture](./docs/source/concepts/architecture.md)
- [Capabilities](./docs/source/concepts/capabilities.md)
- [Tutorials](./docs/source/tutorials/index.md)
- [Games](./docs/source/games/index.md)
- [Contributing](./docs/source/contributing/index.md)

## Contributing

See:

- [docs/source/contributing/dev_setup.md](./docs/source/contributing/dev_setup.md)
- [docs/source/contributing/release_process.md](./docs/source/contributing/release_process.md)

## License

MIT. See [LICENSE](./LICENSE).
