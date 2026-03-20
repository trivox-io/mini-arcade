# Configuration Internals

## Purpose

This page explains how YAML config is loaded, merged, normalized, and injected
into runtime for both examples and games.

## Runtime entrypoints that consume config

Games (reference pattern):

- clone/reference games: `games/*/src/<game>/app.py`
- original local games: `originals/*/src/<game>/app.py`
- `Settings.for_game("<game-id>", required=True)`
- `BackendLoader.load_backend(settings.backend_defaults(...))`
- `run_game(engine_config=..., scene_config=..., gameplay_config=...)`

Examples (tutorial pattern):

- `examples/catalog/**/main.py`
- `Settings.for_example("<example-id>", required=False)`
- `ExampleSpec` built from settings + CLI overrides

## Settings loader behavior

Implementation: `packages/mini-arcade/src/mini_arcade/modules/settings/__init__.py`

Key points:

1. Scope-aware profile loading:
   - game:
     - `originals/<game-id>/settings/settings.yml|yaml`
     - `games/<game-id>/settings/settings.yml|yaml`
   - example:
     - shared: `examples/settings/settings.yml|yaml`
     - overlay: `examples/settings/<example-id>.yml|yaml`
2. Merging:
   - deep merge for dict sections
   - later files override earlier files
3. Optional explicit override:
   - constructor `config_path=...`
   - env var `MINI_ARCADE_CONFIG_PATH`
4. Profile caching:
   - `Settings` instances are cached by `(config_path, scope, name)`
   - pass `force_reload=True` if you need a fresh read

## YAML structure used by engine

The framework reads these sections:

- `scene` -> `scene_defaults()`
- `engine_config` -> `engine_config_defaults()`
- `backend` -> `backend_defaults()`
- `gameplay` -> `gameplay_defaults()`

Recommended schema:

```yaml
scene:
  initial_scene: menu
  scene_registry:
    discover_packages:
      - my_game.scenes
      - mini_arcade_core.scenes

engine_config:
  fps: 60
  virtual_resolution: [960, 540]
  enable_profiler: false
  postfx:
    enabled: false
    active: []

backend:
  provider: native # or pygame
  window:
    width: 960
    height: 540
    title: My Game
    resizable: true
  renderer:
    background_color: [20, 20, 20]
  fonts:
    - name: default
      path: ${assets_root}/fonts/my_font.ttf
      size: 24
  audio:
    enable: true
    sounds:
      select: sfx/select.wav

gameplay:
  difficulty:
    default: normal
```

## Path token resolution

Supported placeholders (resolved by `Settings.resolve_path()`):

- `${settings_dir}`
- `${project_root}`
- `${assets_root}`
- `${repo_root}`
- `${cwd}`

`backend_defaults(resolve_paths=True)` resolves:

- `backend.fonts[*].path`
- `backend.audio.sounds[*]` (resolved relative to assets root)

## How config becomes runtime objects

Game bootstrap pattern:

```python
from mini_arcade.modules.backend_loader import BackendLoader
from mini_arcade.modules.settings import Settings
from mini_arcade_core import run_game

settings = Settings.for_game("deja-bounce", required=True)

backend_cfg = settings.backend_defaults(resolve_paths=True)
backend = BackendLoader.load_backend(backend_cfg)

engine_cfg = settings.engine_config_defaults()
scene_cfg = settings.scene_defaults()
gameplay_cfg = settings.gameplay_defaults()

run_game(
    engine_config=engine_cfg,
    scene_config=scene_cfg,
    backend=backend,
    gameplay_config=gameplay_cfg,
)
```

Inside `run_game(...)` (`mini_arcade_core.__init__`):

- `engine_config` dict -> `EngineConfig.from_dict(...)`
- `scene_config` dict -> `SceneConfig.from_dict(...)`
- `SceneRegistry.discover(*scene_cfg.discover_packages)`
- `Engine(...).run(initial_scene=scene_cfg.initial_scene)`

## CLI interaction with YAML

Examples:

- CLI `--pass-through` values are parsed by `examples/_shared/run_example.py`
- builder code merges them on top of settings values

Games:

- CLI runner forwards `--pass-through` args to game `manage.py`
- if your game parses args, those can override YAML at game level
- the current reference games primarily rely on YAML + internal code defaults

## Where to look in repository

- settings loader:
  `packages/mini-arcade/src/mini_arcade/modules/settings/__init__.py`
- backend loader:
  `packages/mini-arcade/src/mini_arcade/modules/backend_loader/__init__.py`
- game launch wiring:
  `games/deja-bounce/src/deja_bounce/app.py`
  `games/asteroids/src/asteroids/app.py`
  `games/space-invaders/src/space_invaders/app.py`
- example launch wiring:
  `examples/_shared/runner.py`
  `examples/_shared/run_example.py`
