# config/backend_swap

## Goal

Validate backend parity by running the same scene and config envelope on:

- `pygame`
- `native`

This tutorial is about confidence in backend interchangeability for core runtime behavior.

## What this tutorial demonstrates

It uses:

1. Shared example defaults:
   `examples/settings/settings.yml`
2. Example-specific profile:
   `examples/settings/config/backend_swap.yml`
3. Example builder:
   `examples/catalog/config/backend_swap/main.py`
4. Runtime scene:
   `examples/catalog/config/backend_swap/scenes/scene.py`

## Runtime behavior (actual)

`build_example(**kwargs)`:

- loads engine/scene/backend defaults from settings
- reads allowed backends from `backend_swap.backends`
- normalizes `--backend` and falls back to first allowed backend if invalid
- builds one `EngineConfig` + one `SceneConfig`
- injects backend-dependent title suffix (`(... pygame)` or `(... native)`)

The scene then renders runtime values (backend class, fps, virtual resolution, viewport),
so parity checks are visible without extra tooling.

## YAML backend selection (not only CLI)

This tutorial can choose backend without CLI overrides by setting profile YAML:

`examples/settings/config/backend_swap.yml`

```yaml
backend:
  provider: native
```

If you change that to `pygame`, default tutorial execution switches backend:

```bash
mini-arcade run --example config/backend_swap
```

CLI `--backend` remains an override on top of YAML for quick parity testing.

## Parity scope

This tutorial validates:

- window opens/closes cleanly
- virtual resolution is applied equally
- viewport scaling telemetry is coherent
- clear/background behavior is equivalent
- keyboard controls (`F1`, `ESC`) behave the same

This tutorial does not validate:

- game-specific rendering feature parity (sprites/effects in complex games)
- performance parity
- capture/audio parity under heavy load

## Run

Default (uses `backend.provider` from profile):

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

Override timing/resolution:

```bash
mini-arcade run --example config/backend_swap --pass-through --fps 75 --virtual-width 960 --virtual-height 540
```

## Acceptance checklist

Run both backends and compare:

1. `runtime backend` line changes as expected.
2. `virtual_resolution` line is identical for both runs.
3. `window` and `viewport scale` are coherent after resize.
4. No crash/hang on close.
5. `ESC` exits and `F1` toggles debug overlay in both.

## Invalid backend behavior

If `--backend` value is not in `backend_swap.backends`, builder logic falls back
to first allowed backend instead of crashing. This is intentional for robust demos.

## Useful extensions

To harden parity testing:

- add deterministic input playback and compare screenshots
- add a scripted resize sequence and assert viewport metrics
- add backend-specific logs for font/text metrics and draw timings

Developer internals:

- backend architecture:
  [../../concepts/backends.md](../../concepts/backends.md)
- config loading/merge rules:
  [../../concepts/configuration.md](../../concepts/configuration.md)

## Common pitfalls

- Forgetting `--pass-through`:
  backend override is not forwarded to example builder.
- Mistaking title suffix for real backend state:
  trust the rendered backend class name line, not window title alone.
- Comparing only startup:
  include resize, debug overlay toggle, and clean shutdown.

## Controls

- `F1`: toggle built-in debug overlay
- `ESC`: exit

## Next step

- Build a project with [../create_game.md](../create_game.md) and use this parity method on your own game.
- Use [../scene/minimal_scene.md](../scene/minimal_scene.md) for a minimal baseline scene before layering gameplay systems.
