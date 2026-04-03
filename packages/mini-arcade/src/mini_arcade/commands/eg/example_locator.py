"""
Example target locator aligned with the stable target architecture.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from venv import logger

from mini_arcade.commands.shared.base_target_locator import (
    BaseTargetLocator,
    TargetSpec,
)


class ExampleLocator(BaseTargetLocator):
    """
    Example locator with CODE-DRIVEN validation. See validate() for the signature.

    :cvar kind: str: The kind of target this locator handles (e.g. "game" or "example").
        Used in error messages and TargetSpec.
    """

    kind = "example"

    def validate(self, target_dir: Path) -> TargetSpec:
        """
        CODE-DRIVEN example validation:

        We do NOT require pyproject.toml.

        Signature for examples:
            - examples/<example_id>/main.py exists
            - OR examples/<example_id>/run_example.py exists
            - Optional: examples/<example_id>/src/ exists (added to PYTHONPATH if present)

        The entrypoint is always the shared runner:
            <repo_root>/examples/_shared/run_example.py

        The example_id is the path under examples root
        (e.g. config/engine_config_basics).
        
        :param target_dir: The directory of the example target to validate.
        :type target_dir: Path
        :return: A TargetSpec if validation is successful.
        :rtype: TargetSpec
        :raises ValueError: If validation fails.
        """
        target_id = target_dir.name

        # detect example module existence (minimal signature)
        has_main = (target_dir / "main.py").exists()
        has_run_file = (target_dir / "run_example.py").exists()
        has_src = (target_dir / "src").exists()

        if not (has_main or has_run_file or has_src):
            logger.error(
                f"Example validation failed for target_id='{target_id}' at '{target_dir}': "
                f"missing main.py, run_example.py, and src/"
            )
            raise ValueError(
                f"Not a Mini Arcade example: expected at least one of "
                f"main.py, run_example.py, or src/ under {target_dir}"
            )

        # shared entrypoint
        examples_root = target_dir.parent  # .../examples
        # If nested, try to find real examples root
        if examples_root.name != "examples":
            p = target_dir
            for _ in range(5):
                p = p.parent
                if p.name == "examples":
                    examples_root = p
                    break

        shared_entry = (examples_root / "_shared" / "run_example.py").resolve()
        if not shared_entry.exists():
            raise ValueError(f"Shared example runner missing: {shared_entry}")

        # derive canonical id relative to examples root parent folder
        # examples/catalog/config/engine_config_basics -> config/engine_config_basics
        try:
            catalog_root = examples_root / "catalog"
            target_id = str(
                target_dir.resolve().relative_to(catalog_root.resolve())
            ).replace("\\", "/")
        except ValueError:
            target_id = target_dir.name

        meta: dict[str, Any] = {
            "example_id": target_id,
            "source_roots": ["src"],  # used by PYTHONPATH builder
        }

        return TargetSpec(
            kind="example",
            target_id=target_id,
            root_dir=target_dir,
            entrypoint=shared_entry,
            meta=meta,
        )
