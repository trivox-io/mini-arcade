"""
Editable-install loader for the compiled native extension.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def _candidate_paths() -> list[Path]:
    current_dir = Path(__file__).resolve().parent
    suffixes = ("*.pyd", "*.so", "*.dylib")
    candidates: list[Path] = []

    for pattern in suffixes:
        candidates.extend(sorted(current_dir.glob("_native" + pattern[1:])))

    for entry in map(Path, sys.path):
        package_dir = entry / "mini_arcade_native_backend"
        if not package_dir.is_dir():
            continue
        try:
            if package_dir.resolve() == current_dir:
                continue
        except FileNotFoundError:
            continue
        for pattern in suffixes:
            candidates.extend(sorted(package_dir.glob("_native" + pattern[1:])))

    return candidates


def _load_extension() -> ModuleType:
    module = sys.modules[__name__]
    for candidate in _candidate_paths():
        spec = importlib.util.spec_from_file_location(__name__, candidate)
        if spec is None or spec.loader is None:
            continue
        module.__file__ = str(candidate)
        module.__loader__ = spec.loader
        module.__spec__ = spec
        spec.loader.exec_module(module)
        return module
    raise ImportError(
        "Could not locate the compiled mini_arcade_native_backend._native extension. "
        "Install or build the native backend so _native*.pyd is available."
    )


_load_extension()
