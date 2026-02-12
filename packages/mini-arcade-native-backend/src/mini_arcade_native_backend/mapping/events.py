"""
Event mapping between native backend events and core events.
This module defines the NativeEventMapper class, which is responsible for
translating events received from the native backend into the standardized event
format used by the mini-arcade core.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional, Tuple

from mini_arcade_core.backend.events import (  # pyright: ignore[reportMissingImports]
    Event,
    EventType,
)
from mini_arcade_core.backend.sdl_map import (  # pyright: ignore[reportMissingImports]
    SDL_KEYCODE_TO_KEY,
)

# Justification: native is a compiled extension module.
# pylint: disable=no-name-in-module
from mini_arcade_native_backend import _native as native  # type: ignore


# Justification: Using a dataclass to hold optional fields for event mapping.
# pylint: disable=too-many-instance-attributes
@dataclass
class _Fields:
    key: Optional[int] = None
    key_code: Optional[int] = None
    scancode: Optional[int] = None
    mod: Optional[int] = None
    repeat: Optional[bool] = None

    x: Optional[int] = None
    y: Optional[int] = None
    dx: Optional[int] = None
    dy: Optional[int] = None

    button: Optional[int] = None
    wheel: Optional[Tuple[int, int]] = None
    size: Optional[Tuple[int, int]] = None
    text: Optional[str] = None


# pylint: enable=too-many-instance-attributes


class NativeEventMapper:
    """
    Maps native backend events to core events.

    :param native_mod: The native backend module providing event definitions.
    :type native_mod: module
    """

    def __init__(self, native_mod: native):
        self._native = native_mod
        self._map = {
            native_mod.EventType.Unknown: EventType.UNKNOWN,
            native_mod.EventType.Quit: EventType.QUIT,
            native_mod.EventType.KeyDown: EventType.KEYDOWN,
            native_mod.EventType.KeyUp: EventType.KEYUP,
            native_mod.EventType.MouseMotion: EventType.MOUSEMOTION,
            native_mod.EventType.MouseButtonDown: EventType.MOUSEBUTTONDOWN,
            native_mod.EventType.MouseButtonUp: EventType.MOUSEBUTTONUP,
            native_mod.EventType.MouseWheel: EventType.MOUSEWHEEL,
            native_mod.EventType.WindowResized: EventType.WINDOWRESIZED,
            native_mod.EventType.TextInput: EventType.TEXTINPUT,
        }
        self._handlers: Dict[EventType, Callable[[native.Event], _Fields]] = {
            EventType.KEYDOWN: self._key_event,
            EventType.KEYUP: self._key_event,
            EventType.MOUSEMOTION: self._mouse_motion,
            EventType.MOUSEBUTTONDOWN: self._mouse_button,
            EventType.MOUSEBUTTONUP: self._mouse_button,
            EventType.MOUSEWHEEL: self._mouse_wheel,
            EventType.WINDOWRESIZED: self._window_resized,
            EventType.TEXTINPUT: self._text_input,
        }

    def to_core(self, ev: native.Event) -> Event:
        """
        Maps a native event to a core event.

        :param ev: The native event to map.
        :type ev: native.Event
        :return: The mapped core event.
        :rtype: Event
        """
        etype = self._map.get(ev.type, EventType.UNKNOWN)
        fields = self._handlers.get(etype, self._noop)(ev)

        return Event(
            type=etype,
            key=fields.key,
            key_code=fields.key_code,
            scancode=fields.scancode,
            mod=fields.mod,
            repeat=fields.repeat,
            x=fields.x,
            y=fields.y,
            dx=fields.dx,
            dy=fields.dy,
            button=fields.button,
            wheel=fields.wheel,
            size=fields.size,
            text=fields.text,
        )

    def _noop(self, _ev: native.Event) -> _Fields:
        return _Fields()

    def _key_event(self, ev: native.Event) -> _Fields:
        raw_key = int(getattr(ev, "key", 0) or 0)
        scancode = int(ev.scancode) if getattr(ev, "scancode", 0) else None
        mod = int(ev.mod) if getattr(ev, "mod", 0) else None
        rep = int(getattr(ev, "repeat", 0) or 0)

        return _Fields(
            key_code=raw_key or None,
            key=SDL_KEYCODE_TO_KEY.get(raw_key) if raw_key else None,
            scancode=scancode,
            mod=mod,
            # only meaningful for KEYDOWN; KEYUP will ignore it at the Event construction level
            repeat=bool(rep),
        )

    def _mouse_motion(self, ev: native.Event) -> _Fields:
        return _Fields(x=int(ev.x), y=int(ev.y), dx=int(ev.dx), dy=int(ev.dy))

    def _mouse_button(self, ev: native.Event) -> _Fields:
        return _Fields(
            button=int(ev.button) if getattr(ev, "button", 0) else None,
            x=int(ev.x),
            y=int(ev.y),
        )

    def _mouse_wheel(self, ev: native.Event) -> _Fields:
        wx = int(ev.wheel_x)
        wy = int(ev.wheel_y)
        return _Fields(wheel=(wx, wy) if (wx or wy) else None)

    def _window_resized(self, ev: native.Event) -> _Fields:
        w = int(ev.width)
        h = int(ev.height)
        return _Fields(size=(w, h) if (w and h) else None)

    def _text_input(self, ev: native.Event) -> _Fields:
        t = getattr(ev, "text", "")
        return _Fields(text=t or None)
