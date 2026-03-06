# config/backend_swap

## Goal

Validate backend parity by running the same scene/config with different backend
providers (`pygame` and `native`).

## What this tutorial demonstrates

This tutorial uses:

1. Shared defaults:
   `examples/settings/settings.yml`
2. Example-specific overrides:
   `examples/settings/config/backend_swap.yml`
3. Example builder:
   `examples/catalog/config/backend_swap/main.py`
4. Runtime scene:
   `examples/catalog/config/backend_swap/scenes/scene.py`

Flow:

1. Load defaults from settings.
2. Pick backend (`provider` from config, or CLI `--backend` override).
3. Build one `EngineConfig` and one `SceneConfig`.
4. Run scene `backend_swap` and compare runtime output between backends.

## Run

Default (uses `provider` from settings profile):

```bash
mini-arcade run --example config/backend_swap
```

Force pygame:

```bash
mini-arcade run --example config/backend_swap --pass-through --backend pygame
```

Force native:

```bash
mini-arcade run --example config/backend_swap --pass-through --backend native
```

Optional config override:

```bash
mini-arcade run --example config/backend_swap --pass-through --fps 75 --virtual-width 960 --virtual-height 540
```

## Parity checklist

- Window opens/closes cleanly.
- Same virtual resolution is applied.
- Same clear/background color is applied.
- Input/ESC exit behavior is equivalent.

## Controls

- `F1`: toggle built-in debug overlay
- `ESC`: exit

## Next step

- Build a new project with [Create a Game](../create_game.md).
