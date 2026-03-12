"""
Module providing runtime adapters for window and scene management.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from mini_arcade_core.backend.events import Event, EventType
from mini_arcade_core.backend.keys import Key
from mini_arcade_core.runtime.input.input_port import InputPort
from mini_arcade_core.runtime.input_frame import ButtonState, InputFrame


@dataclass
class InputAdapter(InputPort):
    """Adapter for processing input events."""

    _down: set[Key] = field(default_factory=set)
    _buttons_down: set[str] = field(default_factory=set)
    _axes: dict[str, float] = field(default_factory=dict)
    _mouse_pos: tuple[int, int] = (0, 0)

    # pylint: disable=too-many-locals,too-many-branches
    def build(
        self, events: list[Event], frame_index: int, dt: float
    ) -> InputFrame:
        pressed: set[Key] = set()
        released: set[Key] = set()
        buttons_pressed: set[str] = set()
        buttons_released: set[str] = set()
        quit_req = False
        mouse_dx = 0
        mouse_dy = 0
        text_parts: list[str] = []

        for ev in events:
            if ev.type == EventType.QUIT:
                quit_req = True

            elif ev.type == EventType.KEYDOWN and ev.key is not None:
                if ev.key not in self._down:
                    pressed.add(ev.key)
                self._down.add(ev.key)

            elif ev.type == EventType.KEYUP and ev.key is not None:
                if ev.key in self._down:
                    self._down.remove(ev.key)
                released.add(ev.key)

            elif ev.type == EventType.ACTIONDOWN and ev.action:
                if ev.action not in self._buttons_down:
                    buttons_pressed.add(ev.action)
                self._buttons_down.add(ev.action)

            elif ev.type == EventType.ACTIONUP and ev.action:
                if ev.action in self._buttons_down:
                    self._buttons_down.remove(ev.action)
                buttons_released.add(ev.action)

            elif ev.type == EventType.AXISMOTION and ev.axis:
                self._axes[ev.axis] = float(ev.value or 0.0)

            elif ev.type == EventType.MOUSEMOTION:
                x = int(ev.x) if ev.x is not None else self._mouse_pos[0]
                y = int(ev.y) if ev.y is not None else self._mouse_pos[1]
                self._mouse_pos = (x, y)
                mouse_dx += int(ev.dx or 0)
                mouse_dy += int(ev.dy or 0)

            elif ev.type in (
                EventType.MOUSEBUTTONDOWN,
                EventType.MOUSEBUTTONUP,
            ):
                if ev.x is not None and ev.y is not None:
                    self._mouse_pos = (int(ev.x), int(ev.y))

            elif ev.type == EventType.TEXTINPUT and ev.text:
                text_parts.append(str(ev.text))

        buttons: dict[str, ButtonState] = {}
        all_buttons = self._buttons_down | buttons_pressed | buttons_released
        for name in all_buttons:
            buttons[name] = ButtonState(
                down=name in self._buttons_down,
                pressed=name in buttons_pressed,
                released=name in buttons_released,
            )

        return InputFrame(
            frame_index=frame_index,
            dt=dt,
            keys_down=frozenset(self._down),
            keys_pressed=frozenset(pressed),
            keys_released=frozenset(released),
            buttons=buttons,
            axes=dict(self._axes),
            mouse_pos=self._mouse_pos,
            mouse_delta=(mouse_dx, mouse_dy),
            text_input="".join(text_parts),
            quit=quit_req,
        )
