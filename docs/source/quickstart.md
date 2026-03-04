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
python -m mini_arcade.main run --example 001_min_scene
```

### 3) Run a game

```bash
python -m mini_arcade.main run --game deja-bounce
```

### 4) Run tests

```bash
pytest
```
