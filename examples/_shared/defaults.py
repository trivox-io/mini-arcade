"""
Shared helpers for example specs (defaults).
"""

from __future__ import annotations


def make_default_backend_factory(*, title: str):
    """
    Return a backend_factory() that builds a default backend config.

    For now: pygame backend (like your current examples).
    Later: choose backend based on kwargs/passthrough.
    """

    def backend_factory():
        from mini_arcade_pygame_backend import (  # type: ignore[import-not-found] pylint: disable=import-outside-toplevel
            PygameBackend,
            PygameBackendSettings,
        )

        settings = PygameBackendSettings.from_dict(
            {
                "window": {
                    "width": 800,
                    "height": 600,
                    "title": title,
                    "resizable": True,
                },
                "renderer": {"background_color": (20, 20, 20)},
            }
        )
        return PygameBackend(settings=settings)

    return backend_factory
