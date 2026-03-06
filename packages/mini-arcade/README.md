# mini-arcade

`mini-arcade` is the user-facing package for running Mini Arcade games and examples.

It provides:

- the CLI entrypoint (`mini-arcade`)
- runner modules for `--game` and `--example`
- integration helpers that connect settings, backends, and runtime launch

## Install

```bash
pip install mini-arcade
```

## CLI

```bash
mini-arcade --help
mini-arcade run --game deja-bounce
mini-arcade run --example config/engine_config_basics
mini-arcade run --example config/backend_swap --pass-through --backend native --fps 72
```

Equivalent module invocation:

```bash
python -m mini_arcade.main run --game deja-bounce
```

## Docs

See monorepo docs in `docs/` for quickstart, architecture, tutorials, and game creation.
