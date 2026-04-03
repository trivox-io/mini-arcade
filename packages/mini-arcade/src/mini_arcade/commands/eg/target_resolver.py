"""
Target resolver for example commands. Resolves CLI args into validated target specs.
"""

from __future__ import annotations

from pathlib import Path

from mini_arcade.utils.logging import logger
from mini_arcade.utils.repo import find_repo_root

from .example_locator import ExampleLocator
from .models import ExampleKwargsType


class TargetResolver:
    """
    Resolves example CLI args into validated target specs.

    :param kwargs: The keyword arguments from the CLI command,
        expected to include 'id' and optionally 'examples_dir'.
    :type kwargs: ExampleKwargsType
    """

    def __init__(self, kwargs: ExampleKwargsType | None = None):
        self.kwargs = kwargs
        repo_root = find_repo_root(Path.cwd())
        default_parent = (
            (repo_root / "examples" / "catalog").resolve()
            if repo_root is not None
            else (Path.cwd() / "examples" / "catalog").resolve()
        )
        self._locator = ExampleLocator(
            dev_default_parent_dir=default_parent
        )

    @property
    def parent_dir(self) -> Path:
        """
        Resolves the parent directory for examples based on kwargs.

        :return: The parent directory for examples.
        :rtype: Path
        """
        if self.kwargs is None:
            raise ValueError(
                "TargetResolver requires kwargs to resolve parent_dir"
            )
        return self._locator.resolve_parent_dir(self.kwargs.examples_dir)

    def resolve(self):
        """
        Resolves the target example based on kwargs.
        """
        if self.kwargs is None:
            raise ValueError("TargetResolver requires kwargs to resolve")
        return self.resolve_id(self.kwargs.id)

    def resolve_id(self, example_id: str):
        """
        Resolves the target example based on the provided example_id and parent_dir.

        :param example_id: The id of the example to resolve (e.g. "config/engine_config_basics").
        :type example_id: str
        :return: The validated target spec for the example.
        :rtype: TargetSpec
        """
        parent = self.parent_dir
        logger.debug(
            f"Resolving target example_id='{example_id}' under parent='{parent}'"
        )
        target_dir = self._locator.find_dir(parent, example_id)
        logger.debug(f"Found target directory: {target_dir}")
        return self._locator.validate(target_dir)
