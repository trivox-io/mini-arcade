"""
Helpers for locating games in the monorepo.
"""

from __future__ import annotations

from pathlib import Path

CLONE_GAMES_DIRNAME = "games"
ORIGINAL_GAMES_DIRNAME = "originals"
LEGACY_GAME_COLLECTION_DIRS: tuple[str, ...] = ("clones", "originals")
DEFAULT_GAME_SCAFFOLD_DESTINATION = ORIGINAL_GAMES_DIRNAME


def _clean_game_id(game_id: str) -> str:
    return str(game_id).replace("\\", "/").strip("/")


def clone_games_root(repo_root: Path) -> Path:
    return Path(repo_root).resolve() / CLONE_GAMES_DIRNAME


def original_games_root(repo_root: Path) -> Path:
    return Path(repo_root).resolve() / ORIGINAL_GAMES_DIRNAME


def _iter_game_dirs_under_one_root(root: Path) -> tuple[Path, ...]:
    """
    Return all game roots under one parent directory.

    Supported layouts:
    - direct children: ``games/<game-id>`` or ``originals/<game-id>``
    - legacy nested children under ``games/clones/<game-id>`` or
      ``games/originals/<game-id>``
    """

    base = Path(root).resolve()
    if not base.exists() or not base.is_dir():
        return ()

    discovered: list[Path] = []
    for child in sorted(base.iterdir(), key=lambda path: path.name):
        if not child.is_dir():
            continue
        if (child / "pyproject.toml").exists():
            discovered.append(child.resolve())
            continue
        if child.name not in LEGACY_GAME_COLLECTION_DIRS:
            continue
        for nested in sorted(child.iterdir(), key=lambda path: path.name):
            if nested.is_dir() and (nested / "pyproject.toml").exists():
                discovered.append(nested.resolve())
    return tuple(discovered)


def iter_repo_game_dirs(
    repo_root: Path,
    *,
    clone: bool | None = None,
) -> tuple[Path, ...]:
    """
    Return all known game roots across repo-level clone and original roots.

    ``clone=True`` limits discovery to ``games/``.
    ``clone=False`` limits discovery to ``originals/``.
    ``clone=None`` searches originals first, then clones.
    """

    repo = Path(repo_root).resolve()
    if clone is True:
        roots = (clone_games_root(repo),)
    elif clone is False:
        roots = (original_games_root(repo),)
    else:
        roots = (original_games_root(repo), clone_games_root(repo))

    discovered: list[Path] = []
    for root in roots:
        discovered.extend(_iter_game_dirs_under_one_root(root))
    return tuple(discovered)


def find_game_dir_under(parent_dir: Path, game_id: str) -> Path | None:
    """
    Resolve one game root by id under a specific parent directory.
    """

    root = Path(parent_dir).resolve()
    clean = _clean_game_id(game_id)
    if not clean:
        return None

    direct = (root / Path(clean)).resolve()
    if (direct / "pyproject.toml").exists():
        return direct

    basename = Path(clean).name
    matches = [
        path for path in _iter_game_dirs_under_one_root(root)
        if path.name == basename
    ]
    if len(matches) == 1:
        return matches[0]
    return None


def find_game_dir(
    repo_root: Path,
    game_id: str,
    *,
    clone: bool | None = None,
) -> Path | None:
    """
    Resolve one game root by id across repo-level clone and original roots.
    """

    clean = _clean_game_id(game_id)
    if not clean:
        return None

    basename = Path(clean).name
    matches = [
        path
        for path in iter_repo_game_dirs(repo_root, clone=clone)
        if path.name == basename
    ]
    if len(matches) == 1:
        return matches[0]
    return None


def game_settings_candidates(
    repo_root: Path,
    game_id: str,
    *,
    clone: bool | None = None,
) -> list[Path]:
    """
    Return likely settings file candidates for one game id across repo roots.
    """

    clean = _clean_game_id(game_id)
    if not clean:
        return []

    candidates: list[Path] = []
    for game_dir in iter_repo_game_dirs(repo_root, clone=clone):
        if game_dir.name != Path(clean).name:
            continue
        base = game_dir / "settings" / "settings"
        candidates.extend(
            [base.with_suffix(".yml"), base.with_suffix(".yaml")]
        )
    return candidates


def iter_repo_game_source_roots(
    repo_root: Path,
    *,
    clone: bool | None = None,
) -> tuple[Path, ...]:
    """
    Return ``src`` roots for all discovered games across repo-level roots.
    """

    roots: list[Path] = []
    for game_dir in iter_repo_game_dirs(repo_root, clone=clone):
        src_dir = game_dir / "src"
        if src_dir.is_dir():
            roots.append(src_dir.resolve())
    return tuple(roots)
