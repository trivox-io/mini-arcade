# mini-arcade-core

`mini-arcade-core` is the simulation-first core of Mini Arcade.

It is backend-agnostic and focuses on:

- scenes as simulation containers
- entities and lightweight component-style data
- systems for input, simulation, and render preparation
- draw packets that backends can replay

Backends are responsible for:

- window and event polling
- drawing primitives, textures, and text
- audio, capture, and frame presentation

## Design goals

- small, explicit API surface
- deterministic simulation patterns
- testable game logic outside the rendering layer
- backend swapping between `native` and `pygame`

## Frame mental model

A typical frame is:

1. gather input and produce intents
2. tick simulation and systems
3. build draw packets
4. let the selected backend render and present the frame

## Install

```bash
pip install mini-arcade-core
```

## Docs

See the monorepo docs for architecture and concepts:

- `docs/source/concepts/architecture.md`
- `docs/source/concepts/capabilities.md`
- `docs/source/tutorials/index.md`
