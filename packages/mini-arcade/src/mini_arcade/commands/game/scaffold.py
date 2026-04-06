"""
Game scaffold implementation owned by the game command domain.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from mini_arcade.cli.exceptions import CommandException
from mini_arcade.commands.shared.scaffold import (
    BaseScaffoldProcessor,
    BaseScaffoldSpec,
    render_template_tree,
)
from mini_arcade.common.game_paths import GAMES_DIRNAME
from mini_arcade.constants import APP

from .models import ScaffoldKwargs


def _dependency_series(version: str) -> str:
    parts = version.split(".")
    if len(parts) < 2:
        return version
    return f"{parts[0]}.{parts[1]}"


def _default_package_name(game_id: str) -> str:
    return game_id.strip().lower().replace("-", "_")


def _default_title(game_id: str) -> str:
    return game_id.replace("-", " ").replace("_", " ").title()


def _validate_game_id(game_id: str) -> str:
    normalized = game_id.strip().lower()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", normalized):
        raise CommandException(
            "id must be kebab-case using letters, numbers, and hyphens"
        )
    return normalized


def _validate_package_name(package: str) -> str:
    normalized = package.strip().lower()
    if not re.fullmatch(r"[a-z_][a-z0-9_]*", normalized):
        raise CommandException(
            "package must be snake_case and start with a letter or underscore"
        )
    return normalized


@dataclass(frozen=True)
class GameScaffoldSpec(BaseScaffoldSpec):
    """
    Specification for generating a Mini Arcade game scaffold.
    """

    game_id: str
    package: str
    title: str
    dependency_series: str


class GameScaffoldProcessor(BaseScaffoldProcessor[GameScaffoldSpec]):
    """
    Processor for creating starter Mini Arcade game projects.
    """

    def __init__(self, **kwargs):
        self.kwargs = ScaffoldKwargs.from_dict(kwargs)
        self.force = bool(self.kwargs.force)
        self.dry_run = bool(self.kwargs.dry_run)

    def _build_spec(self) -> GameScaffoldSpec:
        game_id = _validate_game_id(self.kwargs.id)
        package = _validate_package_name(
            self.kwargs.package or _default_package_name(game_id)
        )
        title = (self.kwargs.title or _default_title(game_id)).strip()
        target_dir = (
            Path(self.kwargs.destination or GAMES_DIRNAME)
            .expanduser()
            .resolve()
            / game_id
        )
        dependency_series = _dependency_series(APP.version)
        return GameScaffoldSpec(
            game_id=game_id,
            package=package,
            title=title,
            target_dir=target_dir,
            dependency_series=dependency_series,
        )

    def _template_files(self, spec: GameScaffoldSpec) -> dict[Path, str]:
        return render_template_tree(
            "game",
            spec.target_dir,
            {
                "dependency_series": spec.dependency_series,
                "game_id": spec.game_id,
                "package": spec.package,
                "title": spec.title,
            },
        )

    def _created_message(self, spec: GameScaffoldSpec) -> str:
        return f"Created game scaffold at {spec.target_dir}"


__all__ = [
    "GameScaffoldProcessor",
    "GameScaffoldSpec",
]
