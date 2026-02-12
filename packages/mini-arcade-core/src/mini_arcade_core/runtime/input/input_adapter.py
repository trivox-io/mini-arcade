"""
Module providing runtime adapters for window and scene management.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from mini_arcade_core.backend.events import Event, EventType
from mini_arcade_core.backend.keys import Key
from mini_arcade_core.runtime.input.input_port import InputPort
from mini_arcade_core.runtime.input_frame import InputFrame


@dataclass
class InputAdapter(InputPort):
    """Adapter for processing input events."""

    _down: set[Key] = field(default_factory=set)

    def build(
        self, events: list[Event], frame_index: int, dt: float
    ) -> InputFrame:
        pressed: set[Key] = set()
        released: set[Key] = set()
        quit_req = False

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

        return InputFrame(
            frame_index=frame_index,
            dt=dt,
            keys_down=frozenset(self._down),
            keys_pressed=frozenset(pressed),
            keys_released=frozenset(released),
            quit=quit_req,
        )
