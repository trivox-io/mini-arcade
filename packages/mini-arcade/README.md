# mini-arcade

`mini-arcade` is the **user-facing entry point** for the Mini Arcade ecosystem.

It provides:

- a **unified namespace** that exposes the core + backends
- **runner utilities** (CLI) to run examples and games
- small shared utilities (logging, helpers, etc.)

## Install

```bash
pip install mini-arcade
```

## Unified namespace

After installing, you can import:

- `mini_arcade.core` → engine core
- `mini_arcade.backends.pygame` → pygame backend
- `mini_arcade.backends.native` → native SDL2 backend

## Run something

```bash
mini-arcade --help
mini-arcade list
mini-arcade run --game <game-name>
mini-arcade run --example <example-name>
```

> Replace commands above with your real CLI. Keep this section updated — it’s the first thing users try.

## Docs

See the monorepo docs in `docs/` (quickstart, concepts, tutorials, games).
