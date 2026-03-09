# config/engine_config_basics

## Goal

Understand how Mini Arcade builds runtime config from:

1. settings files
2. CLI passthrough overrides
3. example builder defaults

This tutorial is the reference for `EngineConfig` + `SceneConfig` wiring.

For full game scaffolding (entities, systems, draw ops), see
[../create_game.md](../create_game.md).

## Why this example matters

Most real projects need:

- backend selection per environment (`pygame` in dev, `native` for parity tests)
- runtime tuning (`fps`, `virtual_resolution`, profiler, postfx) without code edits
- one scene implementation that remains backend-agnostic

This example proves that workflow end-to-end.

## Source map

- Settings profile:
  `examples/settings/config/engine_config_basics.yml`
- Example builder:
  `examples/catalog/config/engine_config_basics/main.py`
- Shared runner:
  `examples/_shared/runner.py`
- Runtime scene:
  `examples/catalog/config/engine_config_basics/scenes/scene.py`

## Runtime flow (actual)

1. CLI resolves example id `config/engine_config_basics`.
2. Shared runner imports `examples.catalog.config.engine_config_basics.main`.
3. `build_example(**kwargs)` loads settings with:
   `Settings.for_example("config/engine_config_basics", required=False)`.
4. Builder merges:
   - shared example defaults (`examples/settings/settings.yml`)
   - example profile (`examples/settings/config/engine_config_basics.yml`)
   - CLI passthrough overrides (`--backend`, `--fps`, etc.)
5. Runner constructs:
   - backend instance via `backend_factory()`
   - `EngineConfig` via `engine_config_factory(...)`
   - `SceneConfig` from `ExampleSpec` fields
6. Scene renders effective runtime values on screen for inspection.

## Config mapping table

| Input key | Source section | Final runtime target |
|---|---|---|
| `backend.provider` / `--backend` | settings + CLI | backend implementation (`NativeBackend` or `PygameBackend`) |
| `engine_config.fps` / `--fps` | settings + CLI | `EngineConfig.fps` |
| `engine_config.virtual_resolution` / `--virtual-width --virtual-height` | settings + CLI | `EngineConfig.virtual_resolution` |
| `engine_config.enable_profiler` / `--enable-profiler` | settings + CLI | `EngineConfig.enable_profiler` |
| `engine_config.postfx.enabled` / `--postfx-enabled` | settings + CLI | `EngineConfig.postfx.enabled` |
| `engine_config.postfx.active` / `--postfx-active` | settings + CLI | `EngineConfig.postfx.active` |
| `scene.initial_scene` | settings | `SceneConfig.initial_scene` |
| `scene.scene_registry.discover_packages` | settings | `SceneConfig.discover_packages` |
| `backend.window.*` / `--window-width --window-height` | settings + CLI | backend window settings |
| `backend.renderer.background_color` | settings | backend renderer settings |

## YAML structure for real games

This example uses example-scoped YAML, but the same model is used by games in:

- `games/<game-id>/settings/settings.yml`

Recommended game profile shape:

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
      path: ${assets_root}/fonts/MyFont.ttf
      size: 24
  audio:
    enable: true
    sounds:
      select: sfx/select.wav

gameplay:
  difficulty:
    default: normal
```

## How YAML gets into the engine/game

Reference flow from current games (`deja-bounce`, `asteroids`, `space-invaders`):

```python
from mini_arcade.modules.backend_loader import BackendLoader
from mini_arcade.modules.settings import Settings
from mini_arcade_core import run_game

settings = Settings.for_game("my-game", required=True)

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

What the framework does with each payload:

- `backend_cfg`:
  selects and configures backend implementation from `backend.provider`
- `engine_cfg`:
  converted to `EngineConfig` (`fps`, virtual resolution, postfx, profiler)
- `scene_cfg`:
  converted to `SceneConfig`, then scene discovery/import runs
- `gameplay_cfg`:
  injected into `GamePlaySettings` and exposed via runtime context

## Deep-dive docs

Developer internals:

- Config system:
  [../../concepts/configuration.md](../../concepts/configuration.md)
- Backend selection/contract:
  [../../concepts/backends.md](../../concepts/backends.md)

## Precedence rules

Highest to lowest:

1. CLI passthrough args
2. Example-specific settings profile
3. Shared example settings profile
4. Hardcoded fallback values in `main.py`

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

Override runtime timing/resolution:

```bash
mini-arcade run --example config/engine_config_basics --pass-through --fps 72 --virtual-width 960 --virtual-height 540
```

Enable profiler + postfx:

```bash
mini-arcade run --example config/engine_config_basics --pass-through --enable-profiler --postfx-enabled --postfx-active crt,vignette_noise
```

## What to verify on-screen

The scene prints these values directly from runtime config/services:

- backend class name
- fps target
- virtual resolution
- postfx enabled + active list
- profiler enabled flag
- real window size + viewport mode + viewport scale

If a CLI override works, those lines change immediately on next launch.

## Practical checks

1. Set `--virtual-width 960 --virtual-height 540` and confirm line changes.
2. Run once on `pygame` and once on `native`; backend line must change, scene code must not.
3. Enable `--postfx-enabled` and pass `--postfx-active` list; scene should display active ids.
4. Resize window and watch viewport telemetry (`mode`, `scale`).

## Common mistakes

- Passing overrides without `--pass-through`:
  args are consumed by the top-level CLI instead of the example runner.
- Forgetting discovery package:
  if `discover_packages` misses your module, scene registration is not found.
- Assuming window size equals virtual resolution:
  they are independent (virtual is simulation/render target, window is presentation).

## Controls

- `F1`: toggle built-in debug overlay
- `ESC`: exit

## Next step

- Continue with [backend_swap.md](backend_swap.md) to validate parity-focused backend checks.
- Continue with [../scene/minimal_scene.md](../scene/minimal_scene.md) for the smallest scene baseline.
