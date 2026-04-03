# mini-arcade

`mini-arcade` is the user-facing package for running Mini Arcade games and examples.

It provides:

- the CLI entrypoint (`mini-arcade`)
- grouped commands for examples, games, and systems
- integration helpers that connect settings, backends, and runtime launch

## Install

```bash
pip install mini-arcade
```

## CLI

```bash
mini-arcade --help
mini-arcade game --name deja-bounce
mini-arcade eg --id config/engine_config_basics
mini-arcade eg --id config/backend_swap --pass-through --backend native --fps 72
mini-arcade game scaffold --id orbit-garden
mini-arcade system scaffold --id orbit_lab
mini-arcade system --module experiments.orbit_lab.system_lab_case --visual
mini-arcade eg tour
mini-arcade eg tour --group scene
```

Equivalent module invocation:

```bash
python -m mini_arcade.main game --name deja-bounce
```

In the monorepo, prefer the root runner:

```powershell
python .\manage.py game --name deja-bounce
python .\manage.py eg --id config/backend_swap
```

That path wires local workspace sources ahead of installed packages.

## Docs

See monorepo docs in `docs/` for quickstart, architecture, tutorials, and game creation.
