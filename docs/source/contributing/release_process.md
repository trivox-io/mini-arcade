# Release process

Releases are automated by GitHub Actions (`release-major-minor.yml` ->
`reusable-release-stack.yml`).

## Trigger

Manual workflow dispatch with:

- `bump_type`: `patch` | `minor` | `major`
- optional `subtree_repo_owner`

## What the pipeline does

1. Checks out stable branch (`main` by default).
2. Bumps lockstep versions in package `pyproject.toml` files.
3. Aligns inter-package dependency constraints.
4. Updates root `CHANGELOG.md`.
5. Commits and pushes release changes to stable branch.
6. Publishes packages to PyPI in dependency order:
   - `mini-arcade-core`
   - `mini-arcade-pygame-backend`
   - `mini-arcade-native-backend`
   - `mini-arcade`
7. Tags release artifacts:
   - `mini-arcade-core-vX.Y.Z`
   - `mini-arcade-pygame-backend-vX.Y.Z`
   - `mini-arcade-native-backend-vX.Y.Z`
   - `mini-arcade-vX.Y.Z`
8. Creates GitHub Releases with zip assets per package subtree.
9. Syncs `develop` from stable branch.
10. Pushes subtree mirrors to package repos.
11. Sends release notifications (Slack/Discord, if secrets are configured).

## Prerequisites

- PyPI token (`PYPI_API_TOKEN`)
- Subtree push token (`SUBTREE_PUSH_TOKEN`)
- Optional notification secrets for Slack/Discord

## Notes

- Versioning is lockstep across the four published packages.
- Native backend pipeline builds Windows wheels and also publishes sdist.
- Stable/develop branch names are configurable in workflow inputs.
