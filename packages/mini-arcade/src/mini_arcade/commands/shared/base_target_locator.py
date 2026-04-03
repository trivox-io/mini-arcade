"""
Shared target-location primitives for game and example command domains.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from mini_arcade.utils.logging import logger

Kind = Literal["game", "example"]


@dataclass(frozen=True)
class TargetSpec:
    """
    Specification for a target to run.
    """

    kind: Kind
    target_id: str
    root_dir: Path
    entrypoint: Path
    meta: dict[str, Any]


class BaseTargetLocator:
    """
    Base class for resolving one runnable target under a parent directory.
    """

    kind: Kind = "target"

    def __init__(self, *, dev_default_parent_dir: Path):
        self._dev_default_parent_dir = dev_default_parent_dir

    def resolve_parent_dir(self, parent_override: str | None) -> Path:
        """
        Resolve the parent directory for target discovery.
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
        Resolve one target directory under ``parent_dir``.
        """
        target_dir = (parent_dir / target_id).resolve()
        if not target_dir.exists() or not target_dir.is_dir():
            err_text = (
                f"{self.kind.capitalize()} '{target_id}' "
                f"not found under: {parent_dir}"
            )
            logger.error(err_text)
            raise ValueError(err_text)
        return target_dir

    def validate(self, target_dir: Path) -> TargetSpec:
        """
        Validate the resolved target directory and return a ``TargetSpec``.
        """
        raise NotImplementedError
