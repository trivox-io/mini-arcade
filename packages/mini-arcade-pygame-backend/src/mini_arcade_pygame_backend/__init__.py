"""
mini-arcade pygame backend package.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Justification: Need to import core after setting DLL path on Windows
    # pylint: disable=wrong-import-position
    from .config import PygameBackendSettings
    from .pygame_backend import PygameBackend


__all__ = [
    "PygameBackend",
    "PygameBackendSettings",
]


# NOTE: Momentary __getattr__ to avoid circular imports for type hints
# pylint: disable=import-outside-toplevel,possibly-unused-variable
def __getattr__(name: str):
    if name == "PygameBackend":
        from .pygame_backend import PygameBackend

        return PygameBackend

    if name == "PygameBackendSettings":
        from .config import PygameBackendSettings

        return locals()[name]

    raise AttributeError(name)
