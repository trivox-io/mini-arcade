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

### 2) Run an example

```bash
python -m mini_arcade.main run --example config/engine_config_basics
```

### 2b) Run all examples as a guided tour

```bash
python -m mini_arcade.main run tour
```

Useful filters:

```bash
python -m mini_arcade.main run tour --group scene
python -m mini_arcade.main run tour --from-example scene/minimal_scene --to-example scene/pause_overlay_policy
python -m mini_arcade.main run tour --pass-through --backend native
```

### 3) Run a game

```bash
python -m mini_arcade.main run --game deja-bounce
```

### 4) Run tests

```bash
pytest
```

## Build a new game

Use the full guide:

- [Create a Game](tutorials/create_game.md)
