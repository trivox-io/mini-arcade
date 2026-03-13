# Dev setup

## Requirements

- Python `3.9`, `3.10`, or `3.11`
- Git
- PowerShell (Windows workflow is the most maintained path)
- For native backend development on Windows: `vcpkg` plus SDL2 libraries
  available to CMake

## One-command setup (Windows)

```powershell
./scripts/dev_install.ps1
```

This script:

- creates/uses `.venv`
- installs editable package dependencies under `packages/*`
- installs dev tools (`pytest`, `black`, `isort`, `mypy`, `pylint`, `pre-commit`)
- installs docs tooling (Sphinx + extensions)

## Native backend setup

The pygame backend is pure Python. The native backend is not.

`mini_arcade_native_backend` combines:

- Python source from `packages/mini-arcade-native-backend/src`
- a compiled `_native` extension from the active virtual environment

That means editable development has one extra failure mode: Python code can be
newer than the compiled extension. If that happens, imports may succeed while
runtime symbols are missing or out of date.

### Recommended Windows flow with `vcpkg`

1. Install `vcpkg`.
2. Install native dependencies for your triplet, for example:

```powershell
vcpkg install sdl2:x64-windows sdl2-ttf:x64-windows sdl2-mixer:x64-windows
```

3. Run setup with the toolchain environment enabled:

```powershell
./scripts/dev_install.ps1 -SetVcpkgEnv -VcpkgRoot C:\src\vcpkg
```

### Rebuild only the native backend

If you update native backend Python or C++ code and want to resync the active
environment:

```powershell
python -m pip install -e .\packages\mini-arcade-native-backend
```

## Verify installation

```powershell
python -m mini_arcade.main --help
pytest
```

Native backend verification:

```powershell
python .\manage.py run --example config/backend_swap --pass-through --backend native
python .\manage.py run --game space-invaders
```

## Common checks

```powershell
./scripts/check-black.ps1
./scripts/check-isort.ps1
./scripts/check-pylint.ps1
```

## Notes

- Prefer editable installs for package development.
- Run commands from repo root unless noted otherwise.
- Keep tooling consistent across packages: format, lint, type-check, test.
- Explicit `backend.provider: native` configuration is strict. Games should fail
  loudly if native setup is broken rather than silently switching backends.
- The root `manage.py` is the standard local entrypoint because it wires
  workspace `packages/*/src` paths ahead of installed site-packages.
