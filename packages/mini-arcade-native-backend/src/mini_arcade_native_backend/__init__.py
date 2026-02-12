"""
mini-arcade native backend package.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .dlls import setup_windows_dll_search_paths

setup_windows_dll_search_paths()

if TYPE_CHECKING:
    # Justification: Need to import core after setting DLL path on Windows
    # pylint: disable=wrong-import-position
    from .config import NativeBackendSettings
    from .native_backend import NativeBackend

__all__ = [
    "NativeBackend",
    "NativeBackendSettings",
]


# NOTE: Momentary __getattr__ to avoid circular imports for type hints
# pylint: disable=import-outside-toplevel,possibly-unused-variable
def __getattr__(name: str):
    if name == "NativeBackend":
        from .native_backend import NativeBackend

        return NativeBackend

    if name == "NativeBackendSettings":
        from .config import NativeBackendSettings

        return locals()[name]

    raise AttributeError(name)
