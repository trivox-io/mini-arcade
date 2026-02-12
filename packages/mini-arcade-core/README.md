# mini-arcade-core

**mini-arcade-core** is the simulation-first core of Mini Arcade.

It is backend-agnostic and focuses on:

- **scenes** (simulation containers)
- **entities + components** (lightweight data)
- **systems** (input, simulation, render prep)
- **draw calls** (render instructions prepared by the scene)

Backends are responsible for:

- window + event polling
- drawing primitives/sprites
- presenting frames

## Design goals

- tiny API surface, but scalable patterns
- deterministic simulation (replays later)
- testable logic (most game rules run headless)
- backend swapping (native / pygame)

## Frame mental model

A typical frame:

1. gather input → produce intents
2. tick simulation
3. generate draw calls
4. backend renders draw calls

## Install

```bash
pip install mini-arcade-core
```

## Docs

Architecture and concepts live in the monorepo docs (`docs/`).
