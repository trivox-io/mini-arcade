"""
Backend loader module for mini_arcade.
"""

from __future__ import annotations

from typing import Any

from mini_arcade_core.backend import (  # pyright: ignore[reportMissingImports]
    Backend,
)


class BackendLoader:
    """
    Utility class to load and configure backends based on settings.

    This class can be extended in the future to support dynamic backend loading,
    configuration from YAML files, or command-line arguments.
    """

    @staticmethod
    def load_backend(settings: dict[str, Any]) -> Backend:
        """
        Load and configure the appropriate backend based on the provided settings.

        :param settings: A dictionary containing backend configuration,
        including the "provider" key to specify which backend to use.
        :type settings: dict[str, Any]
        :returns: An instance of the configured backend.
            :rtype: Backend
        """
        backend_type = settings.get("provider", "native")

        # pylint: disable=import-outside-toplevel
        if backend_type == "native":
            from mini_arcade_native_backend import (
                NativeBackend,
                NativeBackendSettings,
            )

            backend_settings = NativeBackendSettings.from_dict(settings)
            return NativeBackend(settings=backend_settings)

        if backend_type == "pygame":
            from mini_arcade_pygame_backend import (
                PygameBackend,
                PygameBackendSettings,
            )

            backend_settings = PygameBackendSettings.from_dict(settings)
            return PygameBackend(settings=backend_settings)

        raise ValueError(f"Unsupported backend type: {backend_type}")
