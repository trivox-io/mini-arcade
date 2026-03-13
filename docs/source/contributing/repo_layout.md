# Repo layout

```text
mini-arcade/
|- packages/
|  |- mini-arcade/
|  |- mini-arcade-core/
|  |- mini-arcade-pygame-backend/
|  `- mini-arcade-native-backend/
|- games/
|- examples/
|- docs/
`- scripts/
```

## Conventions

- `packages/`: reusable published packages.
- `games/`: reference games proving engine behavior in real scenarios.
- `examples/`: progressive learning path used by tutorials.
- `docs/`: architecture, guides, and API docs source.
- `scripts/`: local developer automation (install/check helpers).

## Runtime entrypoints

- Root `manage.py` is the normal local entrypoint for examples and games.
- Each game also keeps its own `manage.py` and `app.py` so it remains runnable
  as an isolated package.
- Shared settings live under repo-level `settings/` plus game/example-specific
  settings directories.

## Why the root runner matters

The root runner constructs a `PYTHONPATH` that prefers local `packages/*/src`
and game/example `src` trees. That keeps monorepo development aligned with the
current workspace rather than whatever was last installed into `.venv`.
