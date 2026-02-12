"""
Module for getting the installed package version.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version


def get_package_version(package: str) -> str:
    """
    Return the installed package version.

    This is a thin helper around importlib.metadata.version so games can do:

        from mini_arcade_core import get_package_version
        print(get_package_version("mini-arcade"))

    :return: The version string of the installed package.
    :rtype: str

    :raises PackageNotFoundError: If the package is not installed.
    """
    try:
        return version(package)
    except PackageNotFoundError:  # if running from source / editable
        return "0.0.0"
