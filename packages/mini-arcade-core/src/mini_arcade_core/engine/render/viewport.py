"""
Viewport management for virtual to screen coordinate transformations.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

from mini_arcade_core.utils import logger


class ViewportMode(str, Enum):
    """
    Viewport scaling modes.

    :cvar FIT: Scale to fit within window, preserving aspect ratio (letterbox).
    :cvar FILL: Scale to fill entire window, preserving aspect ratio (crop).
    """

    FIT = "fit"  # letterbox
    FILL = "fill"  # crop


# Justification: Many attributes needed to describe viewport state
# pylint: disable=too-many-instance-attributes
@dataclass(frozen=True)
class ViewportState:
    """
    Current state of the viewport.

    :ivar virtual_w (int): Virtual canvas width.
    :ivar virtual_h (int): Virtual canvas height.
    :ivar window_w (int): Current window width.
    :ivar window_h (int): Current window height.
    :ivar mode (ViewportMode): Current viewport mode.
    :ivar scale (float): Current scale factor.
    :ivar viewport_w (int): Width of the viewport rectangle on screen.
    :ivar viewport_h (int): Height of the viewport rectangle on screen.
    :ivar offset_x (int): X offset of the viewport rectangle on screen.
    :ivar offset_y (int): Y offset of the viewport rectangle on screen.
    """

    virtual_w: int
    virtual_h: int

    window_w: int
    window_h: int

    mode: ViewportMode
    scale: float

    # viewport rect in screen pixels where the virtual canvas lands
    # (can be larger than window in FILL mode -> offsets can be negative)
    viewport_w: int
    viewport_h: int
    offset_x: int
    offset_y: int


# pylint: enable=too-many-instance-attributes


class Viewport:
    """
    Manages viewport transformations between virtual and screen coordinates.
    """

    def __init__(
        self,
        virtual_w: int,
        virtual_h: int,
        mode: ViewportMode = ViewportMode.FIT,
    ):
        """
        :param virtual_w: Virtual canvas width.
        :type virtual_w: int

        :param virtual_h: Virtual canvas height.
        :type virtual_h: int

        :param mode: Viewport scaling mode.
        :type mode: ViewportMode
        """
        self._virtual_w = int(virtual_w)
        self._virtual_h = int(virtual_h)
        self._mode = mode
        self._state: ViewportState | None = None

    def set_virtual_resolution(self, w: int, h: int):
        """
        Set a new virtual resolution.

        :param w: New virtual width.
        :type w: int

        :param h: New virtual height.
        :type h: int
        """
        self._virtual_w = int(w)
        self._virtual_h = int(h)
        if self._state:
            self.resize(self._state.window_w, self._state.window_h)

    def set_mode(self, mode: ViewportMode):
        """
        Set a new viewport mode.

        :param mode: New viewport mode.
        :type mode: ViewportMode
        """
        self._mode = mode
        if self._state:
            self.resize(self._state.window_w, self._state.window_h)

    def resize(self, window_w: int, window_h: int):
        """
        Resize the viewport based on the current window size.

        :param window_w: Current window width.
        :type window_w: int

        :param window_h: Current window height.
        :type window_h: int
        """
        window_w = int(window_w)
        window_h = int(window_h)

        sx = window_w / self._virtual_w
        sy = window_h / self._virtual_h
        scale = min(sx, sy) if self._mode == ViewportMode.FIT else max(sx, sy)

        if self._mode == ViewportMode.FIT:
            vw = int(math.floor(self._virtual_w * scale))
            vh = int(math.floor(self._virtual_h * scale))
        else:  # FILL
            vw = int(math.ceil(self._virtual_w * scale))
            vh = int(math.ceil(self._virtual_h * scale))

        ox = (window_w - vw) // 2
        oy = (window_h - vh) // 2

        self._state = ViewportState(
            virtual_w=self._virtual_w,
            virtual_h=self._virtual_h,
            window_w=window_w,
            window_h=window_h,
            mode=self._mode,
            scale=float(scale),
            viewport_w=vw,
            viewport_h=vh,
            offset_x=ox,
            offset_y=oy,
        )
        logger.debug(
            f"Viewport resized: window=({window_w}x{window_h}), "
            f"virtual=({self._virtual_w}x{self._virtual_h}), "
            f"mode={self._mode}, scale={scale:.3f}, "
            f"viewport=({vw}x{vh})@({ox},{oy})"
        )

    @property
    def state(self) -> ViewportState:
        """
        Get the current viewport state.

        :return: Current ViewportState.
        :rtype: ViewportState

        :raises RuntimeError: If the viewport has not been initialized.
        """
        if self._state is None:
            raise RuntimeError(
                "Viewport not initialized. Call resize(window_w, window_h)."
            )
        return self._state

    def screen_to_virtual(self, x: float, y: float) -> tuple[float, float]:
        """
        Convert screen coordinates to virtual coordinates.

        :param x: X coordinate on the screen.
        :type x: float

        :param y: Y coordinate on the screen.
        :type y: float

        :return: Corresponding virtual coordinates (x, y).
        :rtype: tuple[float, float]
        """
        s = self.state
        return ((x - s.offset_x) / s.scale, (y - s.offset_y) / s.scale)

    def virtual_to_screen(self, x: float, y: float) -> tuple[float, float]:
        """
        Convert virtual coordinates to screen coordinates.

        :param x: X coordinate in virtual space.
        :type x: float

        :param y: Y coordinate in virtual space.
        :type y: float

        :return: Corresponding screen coordinates (x, y).
        :rtype: tuple[float, float]
        """
        s = self.state
        return (s.offset_x + x * s.scale, s.offset_y + y * s.scale)
