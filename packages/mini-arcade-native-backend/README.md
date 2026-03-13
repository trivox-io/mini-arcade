# mini-arcade-native-backend

Native SDL2 backend for `mini-arcade-core`.

This package combines:

- a compiled `_native` extension built with `SDL2` and `pybind11`
- a Python `NativeBackend` adapter that implements the shared backend protocol

The design goal is to keep gameplay logic in Python while moving windowing,
event polling, text, audio, capture, and drawing primitives into a native SDL2
layer.

## Install

```bash
pip install mini-arcade-native-backend
```

## Development notes

In the monorepo, local Python sources may run against a compiled `_native`
extension from the active virtual environment. If you change native backend
code and the extension is stale, rebuild it with:

```powershell
python -m pip install -e .\packages\mini-arcade-native-backend
```

For Windows native builds, the maintained path is `vcpkg` plus:

- `SDL2`
- `SDL2_ttf`
- `SDL2_mixer`

See `docs/source/contributing/dev_setup.md` for the current contributor flow.

## Docs

See the monorepo docs for backend architecture and parity guidance:

- `docs/source/concepts/backends.md`
- `docs/source/tutorials/config/backend_swap.md`
