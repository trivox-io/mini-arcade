from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from mini_arcade.utils.logging import logger

Kind = Literal["game", "example"]


@dataclass(frozen=True)
class TargetSpec:
    """
    Specification for a target (game or example) to run.

    :ivar kind: str: The kind of target ("game" or "example").
    :ivar target_id: str: The id of the target (e.g. game id or example id).
    :ivar root_dir: Path: The root directory of the target.
    :ivar entrypoint: Path: The path to the entrypoint script to execute.
    :ivar meta: dict[str, Any]: The metadata loaded from pyproject.toml (for games)
        or inferred (for examples).
    """

    kind: Kind
    target_id: str
    root_dir: Path
    entrypoint: Path
    meta: dict[str, Any]


class BaseTargetLocator:
    """
    Base class for locating a target (game or example) based on command arguments.

    :cvar kind: str: The kind of target this locator handles (e.g. "game" or "example").
            Used in error messages and TargetSpec.
    """

    kind: Kind = "target"

    def __init__(self, *, dev_default_parent_dir: Path):
        self._dev_default_parent_dir = dev_default_parent_dir

    def resolve_parent_dir(self, parent_override: str | None) -> Path:
        """
        Resolve the parent directory for the target, using the override if provided,
        or falling back to the dev default.

        :param parent_override: An optional string path to override the default parent directory.
        :type parent_override: Optional[str]
        :return: The resolved parent directory as a Path object.
        :rtype: Path
        :raises ValueError: If the provided override path does not exist
            or is not a directory.
        """
        if parent_override:
            p = Path(parent_override).expanduser().resolve()
            if not p.exists() or not p.is_dir():
                raise ValueError(
                    f"Target parent directory is not a directory: {p}"
                )
            return p
        return self._dev_default_parent_dir

    def find_dir(self, parent_dir: Path, target_id: str) -> Path:
        """
        Find the target directory under the parent directory.

        :param parent_dir: The parent directory to search under.
        :type parent_dir: Path
        :param target_id: The id/folder name of the target to find.
        :type target_id: str
        :return: The resolved path to the target directory.
        :rtype: Path
        :raises ValueError: If the target directory does not exist or is not a directory.
        """
        target_dir = (parent_dir / target_id).resolve()
        if not target_dir.exists() or not target_dir.is_dir():
            err_text = f"{self.kind.capitalize()} '{target_id}' not found under: {parent_dir}"
            logger.error(err_text)
            raise ValueError(err_text)
        return target_dir

    def validate(self, target_dir: Path) -> TargetSpec:
        """
        Validate the target directory and return a TargetSpec.

        :param target_dir: The directory of the target to validate.
        :type target_dir: Path
        :return: A TargetSpec instance with the validated target information.
        :rtype: TargetSpec
        """
        raise NotImplementedError
