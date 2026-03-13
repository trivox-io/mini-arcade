# Quickstart

## Users

```bash
pip install mini-arcade
python -m mini_arcade.main --help
```

If your environment exposes the `mini-arcade` command, it should behave
equivalently.

## Contributors

### 1) Install editable packages and tooling

```bash
# Windows (PowerShell)
./scripts/dev_install.ps1
```

If you are working on the native backend and use `vcpkg`, pass the toolchain
root so the editable native build can find SDL2:

```powershell
./scripts/dev_install.ps1 -SetVcpkgEnv -VcpkgRoot C:\src\vcpkg
```

### 2) Run an example

```powershell
python .\manage.py run --example config/engine_config_basics
```

### 2b) Run all examples as a guided tour

```powershell
python .\manage.py run tour
```

Useful filters:

```powershell
python .\manage.py run tour --group scene
python .\manage.py run tour --from-example scene/minimal_scene --to-example scene/pause_overlay_policy
python .\manage.py run tour --pass-through --backend native
```

### 3) Run a game

```powershell
python .\manage.py run --game deja-bounce
```

### 4) Run tests

```bash
pytest
```

### 5) Verify backend wiring

Use `pygame` first if you only need a working contributor environment:

```powershell
python .\manage.py run --example config/backend_swap --pass-through --backend pygame
```

Then verify the native path explicitly:

```powershell
python .\manage.py run --example config/backend_swap --pass-through --backend native
python .\manage.py run --game space-invaders
```

If a game or example configured with `backend.provider: native` fails to start,
rebuild the editable native package in the active environment:

```powershell
python -m pip install -e .\packages\mini-arcade-native-backend
```

## Build a new game

Use the full guide:

- [Create a Game](tutorials/create_game.md)
