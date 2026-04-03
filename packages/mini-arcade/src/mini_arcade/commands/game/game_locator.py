"""
Game target locator aligned with the stable target architecture.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import tomllib  # pyright: ignore[reportMissingImports]
except ModuleNotFoundError:  # py39-310
    import tomli as tomllib  # type: ignore

from mini_arcade.commands.shared.base_target_locator import (
    BaseTargetLocator,
    TargetSpec,
)
from mini_arcade.common.game_paths import find_game_dir_under


class TargetMetadataError(RuntimeError):
    """Raised when target metadata cannot be loaded from ``pyproject.toml``."""


def _load_tool_table(project_dir: Path) -> dict[str, Any]:
    pyproject = project_dir / "pyproject.toml"
    if not pyproject.exists():
        raise TargetMetadataError(f"Missing pyproject.toml: {project_dir}")

    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    tool = data.get("tool", {}) if isinstance(data, dict) else {}

    mini_arcade_tool = tool.get("mini-arcade") or tool.get("mini_arcade")
    if not isinstance(mini_arcade_tool, dict):
        raise TargetMetadataError(
            "Missing [tool.mini-arcade] (or [tool.mini_arcade]) table "
            f"in {pyproject}"
        )

    return mini_arcade_tool


def load_game_meta(game_dir: Path) -> dict[str, Any]:
    """
    Load the ``[tool.mini-arcade.game]`` metadata for one game directory.
    """
    mini_arcade_tool = _load_tool_table(game_dir)
    game = mini_arcade_tool.get("game")
    if not isinstance(game, dict):
        raise TargetMetadataError(
            f"Missing [tool.mini-arcade.game] in {game_dir / 'pyproject.toml'}"
        )
    return game


class GameLocator(BaseTargetLocator):
    """
    Game locator with metadata-driven validation.
    """

    kind = "game"

    def find_dir(self, parent_dir: Path, target_id: str) -> Path:
        """
        Find one game directory under the resolved parent directory.
        """
        target_dir = find_game_dir_under(parent_dir, target_id)
        if target_dir is None:
            raise ValueError(
                f"{self.kind.capitalize()} '{target_id}' not found under: {parent_dir}"
            )
        return target_dir

    def validate(self, target_dir: Path) -> TargetSpec:
        try:
            meta = load_game_meta(target_dir)
        except TargetMetadataError as exc:
            raise ValueError(f"Not a Mini Arcade game: {exc}") from exc

        meta_id = meta.get("id")
        target_id = (
            str(meta_id).strip()
            if isinstance(meta_id, str) and meta_id.strip()
            else target_dir.name
        )

        entry_rel = meta.get("entrypoint", "manage.py")
        if not isinstance(entry_rel, str) or not entry_rel.strip():
            raise ValueError(
                "Invalid [tool.mini-arcade.game].entrypoint in "
                f"{target_dir / 'pyproject.toml'}"
            )

        entrypoint = (target_dir / entry_rel).resolve()
        if not entrypoint.exists() or not entrypoint.is_file():
            raise ValueError(
                f"Entrypoint '{entry_rel}' not found for game "
                f"'{target_id}' in: {target_dir}"
            )

        meta.setdefault("source_roots", ["src"])

        return TargetSpec(
            kind="game",
            target_id=target_id,
            root_dir=target_dir,
            entrypoint=entrypoint,
            meta=meta,
        )


__all__ = [
    "GameLocator",
    "TargetMetadataError",
    "_load_tool_table",
    "load_game_meta",
]
