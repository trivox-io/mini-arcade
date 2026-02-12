"""
Module for discovering and loading packages from a specified directory and namespace.
This module defines the OneLevelPackageLoader class, which can be used to discover and
load packages from a specified directory and namespace. It also defines the
DiscoveredPackage dataclass, which represents a discovered package,
and the load_command_packages function, which is a convenience function for loading
command packages.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DiscoveredPackage:
    """
    Represents a discovered package.

    :ivar import_name: The import name of the package
        (e.g. "mini_arcade.modules.game_runner")."
    :ivar path: The filesystem path to the package.
    """

    import_name: str
    path: Path


class ModuleDiscoveryError(RuntimeError):
    """Raised when there is an error discovering modules."""


class ModuleImportError(RuntimeError):
    """Raised when there is an error importing modules."""


class OneLevelPackageLoader:
    """
    Loads packages from a specified directory and namespace.

    :param base_namespace: The base namespace for the packages (e.g. "mini_arcade.modules").
    :type base_namespace: str
    :param base_dir: The base directory to search for packages.
    :type base_dir: str | Path
    :param require_init: Whether to require an __init__.py file in each package (default: True).
    :type require_init: bool
    :param strict: Whether to raise an error if a package fails to import (default: True).
    :type strict: bool
    :param import_commands_fallback: Whether to attempt importing <package>.commands as a
        fallback (default: False).
    :type import_commands_fallback: bool
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        *,
        base_namespace: str,
        base_dir: str | Path,
        require_init: bool = True,
        strict: bool = True,
        import_commands_fallback: bool = False,
    ):
        self.base_namespace = base_namespace.strip(".")
        self.base_dir = Path(base_dir).resolve()
        self.require_init = require_init
        self.strict = strict
        self.import_commands_fallback = import_commands_fallback

        if not self.base_dir.exists() or not self.base_dir.is_dir():
            raise ModuleDiscoveryError(
                f"base_dir does not exist or is not a dir: {self.base_dir}"
            )

    # pylint: enable=too-many-arguments

    def discover(self) -> list[DiscoveredPackage]:
        """
        Discover packages in the base directory.

        :return: A list of DiscoveredPackage instances.
        :rtype: list[DiscoveredPackage]
        """
        out: list[DiscoveredPackage] = []
        for child in sorted(
            self.base_dir.iterdir(), key=lambda p: p.name.lower()
        ):
            if not child.is_dir():
                continue
            if child.name.startswith(("_", ".")):
                continue
            if self.require_init and not (child / "__init__.py").exists():
                continue
            out.append(
                DiscoveredPackage(
                    import_name=f"{self.base_namespace}.{child.name}",
                    path=child,
                )
            )
        return out

    def load_all(self) -> list[DiscoveredPackage]:
        """
        Load all discovered packages.

        :return: A list of successfully loaded DiscoveredPackage instances.
        :rtype: list[DiscoveredPackage]
        :raises ModuleImportError: If strict is True and a package fails to import.
        """
        loaded: list[DiscoveredPackage] = []
        for pkg in self.discover():
            try:
                # Primary: import the package (executes __init__.py)
                importlib.import_module(pkg.import_name)

                # Optional fallback: import <pkg>.commands if you want
                if self.import_commands_fallback:
                    try:
                        importlib.import_module(f"{pkg.import_name}.commands")
                    except ModuleNotFoundError:
                        pass

                loaded.append(pkg)
            except Exception as e:  # pylint: disable=broad-exception-caught
                if self.strict:
                    raise ModuleImportError(
                        f"Failed to import {pkg.import_name} from {pkg.path}"
                    ) from e
        return loaded


def load_command_packages(
    *,
    base_namespace: str,
    base_dir: str | Path,
    strict: bool = True,
) -> list[DiscoveredPackage]:
    """
    Load command packages from the specified directory and namespace.

    :param base_namespace: The base namespace for the command packages (e.g. "mini_arcade.modules").
    :type base_namespace: str
    :param base_dir: The base directory to search for command packages.
    :type base_dir: str | Path
    :param strict: Whether to raise an error if a package fails to import (default: True).
    :type strict: bool
    :return: A list of successfully loaded DiscoveredPackage instances.
    :rtype: list[DiscoveredPackage]
    """
    return OneLevelPackageLoader(
        base_namespace=base_namespace,
        base_dir=base_dir,
        strict=strict,
        import_commands_fallback=False,  # keep your rule
    ).load_all()
