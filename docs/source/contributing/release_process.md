# Release process (planned)

> TODO — keep this aligned with your actual CI.

## Goals

- run tests/lint/type checks across all packages
- publish packages in dependency order
- generate docs
- package games for distribution (itch.io, etc.)

## Dependency order

1. `mini-arcade-core`
2. backends (`mini-arcade-pygame-backend`, `mini-arcade-native-backend`)
3. `mini-arcade` (meta/user-facing package)
