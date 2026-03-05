"""
Shared helpers for example specs (defaults).
"""

from __future__ import annotations


def make_backend_factory(
    *,
    title: str,
    backend: str = "pygame",
    width: int = 800,
    height: int = 600,
    resizable: bool = True,
    background_color: tuple[int, int, int] = (20, 20, 20),
):
    """
    Return a backend factory that can build pygame or native backends.

    :param title: The title of the window.
    :type title: str
    :param backend: Backend id ("pygame" or "native")
    :type backend: str
    :return: A backend factory function.
    :rtype: Callable[[], Backend]
    """

    def backend_factory():
        cfg = {
            "window": {
                "width": int(width),
                "height": int(height),
                "title": title,
                "resizable": bool(resizable),
            },
            "renderer": {"background_color": background_color},
        }

        if backend == "native":
            from mini_arcade_native_backend import (  # type: ignore[import-not-found] pylint: disable=import-outside-toplevel
                NativeBackend,
                NativeBackendSettings,
            )

            settings = NativeBackendSettings.from_dict(cfg)
            return NativeBackend(settings=settings)

        from mini_arcade_pygame_backend import (  # type: ignore[import-not-found] pylint: disable=import-outside-toplevel
            PygameBackend,
            PygameBackendSettings,
        )

        settings = PygameBackendSettings.from_dict(cfg)
        return PygameBackend(settings=settings)

    return backend_factory


def make_default_backend_factory(*, title: str):
    """
    Backwards-compatible alias for pygame default backend factory.
    """
    return make_backend_factory(title=title, backend="pygame")
