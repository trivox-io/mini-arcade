# mini-arcade-native-backend

Native SDL2 backend for **mini-arcade-core**, implemented in C++ with `SDL2` + `pybind11`
and exposed to Python as a backend that plugs into your mini-arcade game framework.

The goal of this repo is to provide a **native window + input + drawing layer** while
keeping all game logic in Python (via `mini-arcade-core`).

- C++ (`SDL2` + `pybind11`) ⇒ `_native` extension module
- Python adapter ⇒ `NativeBackend` implementing `mini_arcade_core.backend.Backend`

## Install

```bash
pip install mini-arcade-native-backend
```

## Docs

Architecture and concepts live in the monorepo docs (`docs/`).
