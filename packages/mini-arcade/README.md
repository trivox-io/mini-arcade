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
mini-arcade scaffold-system-lab --lab-id orbit_lab
mini-arcade system-lab --module experiments.orbit_lab.system_lab_case --visual
mini-arcade run tour
mini-arcade run tour --group scene
```

Equivalent module invocation:

```bash
python -m mini_arcade.main run --game deja-bounce
```

In the monorepo, prefer the root runner:

```powershell
python .\manage.py run --game deja-bounce
python .\manage.py run --example config/backend_swap
```

That path wires local workspace sources ahead of installed packages.

## Docs

See monorepo docs in `docs/` for quickstart, architecture, tutorials, and game creation.
