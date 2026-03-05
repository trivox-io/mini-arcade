# config/engine_config_basics

## Goal

Introduce engine configuration through `GameConfig` and show backend swapping
using the same example id.

## Step by step

1. Build an example spec in `examples/catalog/config/engine_config_basics/main.py`.
2. Read passthrough options (`backend`, `fps`, virtual/window size, postfx, profiler).
3. Build backend from a shared backend factory.
4. Build `GameConfig` with a custom `game_config_factory`.
5. Run scene `engine_config_basics` and display effective runtime config values.

## Run

Default:

```bash
mini-arcade run --example config/engine_config_basics
```

Swap backend:

```bash
mini-arcade run --example config/engine_config_basics --pass-through -- --backend pygame
mini-arcade run --example config/engine_config_basics --pass-through -- --backend native
```

Override config:

```bash
mini-arcade run --example config/engine_config_basics --pass-through -- --fps 72 --virtual-width 960 --virtual-height 540
```

## Concepts covered

- `GameConfig` as current engine config surface
- Backend selection from runner passthrough
- Virtual resolution vs window size
- PostFX defaults (`enabled`, `active`)
- Profiler toggle flag

## Controls

- `F1`: Toggle built-in debug overlay
- `ESC`: Exit

