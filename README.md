# Mini Arcade

> A Python-first mini game engine and toolkit to build and ship small arcade games without a giant engine.

[![CI](https://github.com/trivox-io/mini-arcade/actions/workflows/ci.yml/badge.svg)](https://github.com/trivox-io/mini-arcade/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/trivox-io/mini-arcade)](./LICENSE)
[![PyPI](https://img.shields.io/pypi/v/mini-arcade)](https://pypi.org/project/mini-arcade/)
[![Docs](https://img.shields.io/badge/docs-in%20repo-blue)](./docs)

Mini Arcade is a Python-first mini game engine and monorepo for building small arcade games fast.
It solves a practical gap between learning-oriented toy engines and heavyweight production engines.
It is for indie developers, engine learners, and teams who want a clean architecture with swappable backends.

---

## Why this exists

This project started from a simple goal: understand how game engines work by shipping real games.

- Learn engine internals through real runtime code, not only theory
- Ship small games without the complexity of a giant engine
- Keep gameplay logic testable and backend-agnostic
- Build a reusable foundation for games, examples, and devlogs

## Features

- ✅ Game runner helper (`run`) for games and examples
- ✅ Swappable backends: native SDL2 (`pybind11`) and pygame
- ✅ Scene registry + scene stack/overlay model
- ✅ Runtime services: window, scene query, input, render, audio, files, capture
- ✅ Tick-level command queue + cheat manager integration
- ✅ Render pipeline with passes: begin, world, lighting, UI, postfx, end
- ✅ Capture services: screenshots, video frame capture, replay record/playback
- ✅ Virtual resolution + viewport scaling modes
- ✅ Simulation-first systems/entities architecture
- ✅ 2D spaces modules: math, geometry, kinematics, collision/physics helpers
- ✅ Frame timing and profiler hooks
- 🚧 API/CLI polish and docs hardening
- 🔮 Full backend parity for advanced capture and post-processing workflows

## Status

**Current status:** Alpha

This project is currently:

- actively developed
- open to feedback
- not yet recommended for production-critical projects

## Demo

![Deja Bounce screenshot](./games/deja-bounce/screenshots/20260123_165041_647511_pong.png)

```bash
# Run an example from source checkout
python -m mini_arcade.main run --example 001_min_scene

# Run a reference game
python -m mini_arcade.main run --game deja-bounce
```

## Installation

### Requirements

- Python `>=3.9,<3.12`
- Windows and Linux are currently the most validated environments
- Native backend requires SDL2 libraries (`SDL2`, `SDL2_ttf`, `SDL2_mixer`)

### Install from package manager

```bash
pip install mini-arcade
```

### Install from source

```bash
git clone https://github.com/trivox-io/mini-arcade.git
cd mini-arcade

# Windows (PowerShell)
./scripts/dev_install.ps1
```

## Quick Start

```bash
python -m mini_arcade.main run --example 001_min_scene
python -m mini_arcade.main run --game deja-bounce
```

Expected output: the runner resolves the target, prints the chosen entrypoint/PYTHONPATH, and launches the game window.

## Usage

### Common use cases

#### 1. Basic usage

```bash
python -m mini_arcade.main run --game space-invaders
```

#### 2. Advanced usage

```bash
python -m mini_arcade.main run \
  --example 002_hello_overlay \
  --examples_dir ./examples/scenes \
  --pass_through -- --backend native
```

#### 3. Library/API usage

```python
from mini_arcade_core import GameConfig, SceneRegistry, run_game
from mini_arcade_pygame_backend import PygameBackend, PygameBackendSettings

scene_registry = SceneRegistry(_factories={}).discover(
    "my_game.scenes",
    "mini_arcade_core.scenes",
)

backend_settings = PygameBackendSettings.from_dict(
    {
        "window": {"width": 800, "height": 600, "title": "My Game"},
        "renderer": {"background_color": (20, 20, 20)},
    }
)
backend = PygameBackend(settings=backend_settings)

game_config = GameConfig(
    initial_scene="main",
    fps=60,
    backend=backend,
    virtual_resolution=(800, 600),
)

run_game(game_config=game_config, scene_registry=scene_registry)
```

## Configuration

Configuration is split across CLI flags, game metadata, and runtime config objects.

- CLI flags (`run`): `--game`, `--example`, `--from_source`, `--examples_dir`, `--pass_through`
- Game metadata (`pyproject.toml`): `[tool.mini-arcade.game]` (id, entrypoint, source_roots)
- Runtime config (`GameConfig`): scene, fps, backend, virtual resolution, postfx, profiler

```toml
[tool.mini-arcade.game]
id = "deja-bounce"
entrypoint = "manage.py"
source_roots = ["src"]
```

```python
from mini_arcade_core import GameConfig

cfg = GameConfig(
    initial_scene="main",
    fps=60,
    virtual_resolution=(800, 600),
    enable_profiler=False,
)
```

## Project Structure

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
|- scripts/
|- CHANGELOG.md
`- README.md
```

- `packages/`: engine core, backends, and user-facing package
- `games/`: reference games validating real engine features
- `examples/`: progressive scene/tutorial examples
- `docs/`: Sphinx source of truth
- `scripts/`: local dev/install/lint helpers

## Documentation

- [Quickstart](./docs/source/quickstart.md)
- [Architecture](./docs/source/concepts/architecture.md)
- [Capabilities](./docs/source/concepts/capabilities.md)
- [Tutorials](./docs/source/tutorials/index.md)
- [Games](./docs/source/games/index.md)
- [Contributing Docs](./docs/source/contributing/index.md)
- [FAQ](#faq)

## Roadmap

Planned milestones:

- [ ] Improve CLI ergonomics and command coverage
- [ ] Expand tutorial progression beyond baseline examples
- [ ] Improve backend parity for capture/postfx features
- [ ] Harden API stability for a production-ready `v2.0`

## Contributing

Contributions are welcome.

Please:

1. Read the contributing docs: [docs/source/contributing/index.md](./docs/source/contributing/index.md)
2. Check existing issues before opening a new one
3. Open an issue/discussion for major changes first

### Development setup

```bash
git clone https://github.com/trivox-io/mini-arcade.git
cd mini-arcade

# Windows (PowerShell)
./scripts/dev_install.ps1
```

## Running Tests

```bash
pytest
```

## Code Style

- Formatter: Black
- Import sorting: isort
- Linter: pylint
- Type checking: mypy

```bash
# Windows (PowerShell)
./scripts/check-black.ps1
./scripts/check-isort.ps1
./scripts/check-pylint.ps1
```

## Security

If you discover a security issue, do not open a public issue.

Please report it privately to `rincores@gmail.com` until a dedicated `SECURITY.md` process is published.

## Code of Conduct

A dedicated Code of Conduct file is planned.

Until then, please keep all collaboration respectful and constructive.

## FAQ

### Is this production-ready?

Not yet. The project is in Alpha and APIs/CLI may still evolve.

### Does it support Windows / macOS / Linux?

Windows and Linux are currently the most validated. macOS support is a target, but less validated in this repo today.

### Why did you build this?

To understand engine architecture deeply and still ship small games quickly without relying on a heavyweight engine stack.

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for release history.

## Maintainers

- Santiago Rincon - Creator and maintainer

## Acknowledgments

- Inspired by classic arcade game design and small-engine workflows
- Built with Python, SDL2, pygame, and pybind11
- Thanks to open-source maintainers and contributors

## License

This project is licensed under the MIT License.

See [LICENSE](./LICENSE).
