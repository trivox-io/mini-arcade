# Dev setup

## Requirements

- Python `3.9`, `3.10`, or `3.11`
- Git
- PowerShell (Windows workflow is the most maintained path)

For native backend development you also need SDL2 dependencies.

## One-command setup (Windows)

```powershell
./scripts/dev_install.ps1
```

This script:

- creates/uses `.venv`
- installs editable package dependencies under `packages/*`
- installs dev tools (`pytest`, `black`, `isort`, `mypy`, `pylint`, `pre-commit`)
- installs docs tooling (Sphinx + extensions)

## Verify installation

```powershell
python -m mini_arcade.main --help
pytest
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
