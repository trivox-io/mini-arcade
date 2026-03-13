# Backends Internals

## Purpose

This page explains how backend implementations are selected and used by the
engine at runtime.

## Backend protocol (core contract)

Core interface:

- `packages/mini-arcade-core/src/mini_arcade_core/backend/backend.py`

A backend must expose these ports:

- `window`
- `input`
- `render`
- `text`
- `audio`
- `capture`

And these methods:

- `init()`
- `set_viewport_transform(offset_x, offset_y, scale)`
- `clear_viewport_transform()`

Core code talks only to this protocol, not to pygame/SDL APIs directly.

## Runtime selection

Selection happens in:

- `packages/mini-arcade/src/mini_arcade/modules/backend_loader/__init__.py`

Behavior:

- `backend.provider: native` -> `NativeBackend`
- `backend.provider: pygame` -> `PygameBackend`
- unknown provider -> `ValueError`
- explicit `native` selection is strict; if native initialization is broken, the
  caller should see the error instead of silently switching backends

So yes, backend can be selected directly in YAML:

```yaml
backend:
  provider: native
```

and then overridden by CLI in examples:

```bash
mini-arcade run --example config/backend_swap --pass-through --backend pygame
```

Important distinction:

- Games should honor the configured backend exactly.
- Some examples intentionally sanitize invalid CLI overrides for demo
  robustness, but that is example-specific behavior, not global backend policy.

## Backend settings mapping

Config classes:

- pygame:
  `packages/mini-arcade-pygame-backend/src/mini_arcade_pygame_backend/config.py`
- native:
  `packages/mini-arcade-native-backend/src/mini_arcade_native_backend/config.py`
- shared low-level settings:
  `packages/mini-arcade-core/src/mini_arcade_core/backend/config.py`

Expected dict sections:

- `window`
- `renderer`
- `fonts` (list)
- `audio`

Both backend settings classes support `.from_dict(...)`.

## Runtime integration in Engine

Engine wiring:

- `packages/mini-arcade-core/src/mini_arcade_core/engine/game.py`

At startup:

1. backend instance is provided to `EngineDependencies`
2. `Engine` creates runtime adapters/services around that backend
3. engine loop (`EngineRunner`) polls input and executes render pipeline through backend ports

## Pygame backend notes

Implementation:

- `packages/mini-arcade-pygame-backend/src/mini_arcade_pygame_backend/pygame_backend.py`

Highlights:

- initializes pygame + fonts
- creates ports (`WindowPort`, `InputPort`, `RenderPort`, `TextPort`, etc.)
- uses configured background color/fonts/audio

## Native backend notes

Implementation:

- `packages/mini-arcade-native-backend/src/mini_arcade_native_backend/native_backend.py`

Highlights:

- initializes compiled native backend (`_native`)
- maps python settings to native config
- supports default font fallback resolution if font path not configured
- in editable development, the `_native.py` shim loads the compiled extension
  from the active environment so repo Python sources can work with an installed
  `_native*.pyd`

Practical consequence:

- if native Python code changes but the compiled extension is stale, rebuild the
  package in the current environment with
  `python -m pip install -e .\packages\mini-arcade-native-backend`

## Backend parity expectations

The API is shared, but behavior can still diverge in edge cases.

Use parity tutorials and reference games to validate:

- same scene behavior under both providers
- viewport scaling and window lifecycle parity
- text measurement/drawing consistency for UI-heavy scenes

Recommended parity tutorial:

- `docs/source/tutorials/config/backend_swap.md`
