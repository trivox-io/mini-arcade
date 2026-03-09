"""
Module providing runtime adapters for window and scene management.
"""

from __future__ import annotations

from mini_arcade_core.backend import Backend
from mini_arcade_core.engine.render.viewport import (
    Viewport,
    ViewportMode,
    ViewportState,
)
from mini_arcade_core.runtime.window.window_port import WindowPort
from mini_arcade_core.utils import logger


class WindowAdapter(WindowPort):
    """
    Manages multiple game windows (not implemented).
    """

    _drawable_size: tuple[int, int]

    def __init__(self, backend: Backend):
        self.backend = backend

        self.backend.init()

        w, h = self.backend.window.size()
        dw, dh = self.backend.window.drawable_size()
        self.size = (w, h)
        self._drawable_size = (dw, dh)
        self._initialized = True

        self._viewport = Viewport(w, h, mode=ViewportMode.FIT)
        self._viewport.resize(dw, dh)
        self._apply_viewport_transform()

    def _apply_viewport_transform(self):
        s = self._viewport.state
        # This is the missing link in the new backend design:
        if not hasattr(self.backend, "set_viewport_transform"):
            logger.warning(
                "Backend does not support viewport transforms. "
                "Viewport scaling and offset will not be applied."
            )
            return
        self.backend.set_viewport_transform(s.offset_x, s.offset_y, s.scale)

    def set_virtual_resolution(self, width: int, height: int):
        self._viewport.set_virtual_resolution(int(width), int(height))
        w, h = self.backend.window.size()
        dw, dh = self.backend.window.drawable_size()
        self.size = (w, h)
        self._drawable_size = (dw, dh)
        self._viewport.resize(dw, dh)
        self._apply_viewport_transform()

    def set_viewport_mode(self, mode: ViewportMode):
        self._viewport.set_mode(mode)
        # mode change affects scale/offset
        if self._viewport.state is not None:
            self._apply_viewport_transform()

    def get_viewport(self) -> ViewportState:
        return self._viewport.state

    def screen_to_virtual(self, x: float, y: float) -> tuple[float, float]:
        logical_w, logical_h = self.size
        drawable_w, drawable_h = self._drawable_size

        sx = drawable_w / logical_w if logical_w else 1.0
        sy = drawable_h / logical_h if logical_h else 1.0

        return self._viewport.screen_to_virtual(x * sx, y * sy)

    def set_title(self, title):
        self.backend.window.set_title(title)

    def set_clear_color(self, r, g, b):
        self.backend.render.set_clear_color(r, g, b)

    def on_window_resized(self, width: int, height: int):
        logger.debug(f"Window resized event: {width}x{height}")

        # logical
        logical_w, logical_h = int(width), int(height)

        # drawable (pixel)
        drawable_w, drawable_h = self.backend.window.drawable_size()

        # store both if useful
        self.size = (logical_w, logical_h)
        self._drawable_size = (drawable_w, drawable_h)

        # viewport should match what renderer draws to:
        self._viewport.resize(drawable_w, drawable_h)
        self._apply_viewport_transform()

    def get_virtual_size(self) -> tuple[int, int]:
        s = self.get_viewport()
        return (s.virtual_w, s.virtual_h)
