# Mini Arcade

**Mini Arcade** is a Python-first mini game engine + monorepo built to ship **small, shippable arcade games** while evolving a clean, testable architecture.

It’s also a **learning playground**: every feature is validated through real games and progressive examples, with a focus on a **content pipeline** (screenshots, recordings, replays) for devlogs.

## What’s in here

- **Engine core (`mini-arcade-core`)**: simulation-first scenes, entities, systems
- **Backends**
  - **native (`mini-arcade-native-backend`)**: SDL2 + pybind11
  - **pygame (`mini-arcade-pygame-backend`)**
- **User-facing package (`mini-arcade`)**
  - unified namespace (`mini_arcade.core`, `mini_arcade.backends.*`)
  - CLI runner utilities
- **Games**: Deja Bounce, Space Invaders (and upcoming Asteroids)
- **Examples**: progressive tutorials (meant to become blog posts)

## Install (users)

```bash
pip install mini-arcade
```

## Quick start (dev)

```bash
# Windows (PowerShell)
.\scripts\dev_install.ps1
mini-arcade --help
```

## Docs

Docs live in `docs/` and are the source of truth.

- Quickstart: `docs/quickstart.md`
- Architecture overview: `docs/concepts/architecture.md`
- Tutorials (examples): `docs/tutorials/`
- Games: `docs/games/`

## Repo layout

```text
mini-arcade/
├─ packages/
├─ games/
├─ examples/
└─ docs/
```

## License

See each package for its license (planned: permissive / MIT-style).
