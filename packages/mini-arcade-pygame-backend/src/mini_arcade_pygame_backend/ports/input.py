"""
Input port implementation for the pygame backend.
Provides functionality to poll and map input events.
"""

from __future__ import annotations

import pygame
from mini_arcade_core.backend.events import (  # pyright: ignore[reportMissingImports]
    Event,
    EventType,
)
from mini_arcade_core.backend.keys import Key

PYGAME_KEY_TO_KEY: dict[int, Key] = {
    pygame.K_ESCAPE: Key.ESCAPE,
    pygame.K_RETURN: Key.ENTER,
    pygame.K_SPACE: Key.SPACE,
    pygame.K_TAB: Key.TAB,
    pygame.K_BACKSPACE: Key.BACKSPACE,
    pygame.K_UP: Key.UP,
    pygame.K_DOWN: Key.DOWN,
    pygame.K_LEFT: Key.LEFT,
    pygame.K_RIGHT: Key.RIGHT,
    pygame.K_F1: Key.F1,
    pygame.K_F2: Key.F2,
    pygame.K_F3: Key.F3,
    pygame.K_F4: Key.F4,
    pygame.K_F5: Key.F5,
    pygame.K_F6: Key.F6,
    pygame.K_F7: Key.F7,
    pygame.K_F8: Key.F8,
    pygame.K_F9: Key.F9,
    pygame.K_F10: Key.F10,
    pygame.K_F11: Key.F11,
    pygame.K_F12: Key.F12,
}
# Letters / numbers:
for c in "abcdefghijklmnopqrstuvwxyz":
    PYGAME_KEY_TO_KEY[getattr(pygame, f"K_{c}")] = getattr(Key, c.upper())
for i in range(10):
    PYGAME_KEY_TO_KEY[getattr(pygame, f"K_{i}")] = getattr(Key, f"NUM_{i}")


class InputPort:
    """
    Input port for the Mini Arcade pygame backend.
    """

    def poll(self) -> list[Event]:
        """
        Poll for input events and map them to core events.

        :return: A list of core events.
        :rtype: list[Event]
        """
        out: list[Event] = []
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                out.append(Event(type=EventType.QUIT))

            elif ev.type == pygame.KEYDOWN:
                k = PYGAME_KEY_TO_KEY.get(ev.key)
                out.append(
                    Event(
                        type=EventType.KEYDOWN,
                        key=k,
                        key_code=int(ev.key),
                        scancode=getattr(ev, "scancode", None),
                        mod=getattr(ev, "mod", None),
                        repeat=bool(getattr(ev, "repeat", False)),
                    )
                )

            elif ev.type == pygame.KEYUP:
                k = PYGAME_KEY_TO_KEY.get(ev.key)
                out.append(
                    Event(
                        type=EventType.KEYUP,
                        key=k,
                        key_code=int(ev.key),
                        scancode=getattr(ev, "scancode", None),
                        mod=getattr(ev, "mod", None),
                        repeat=False,
                    )
                )

            elif ev.type == pygame.VIDEORESIZE:
                out.append(
                    Event(
                        type=EventType.WINDOWRESIZED,
                        size=(int(ev.w), int(ev.h)),
                    )
                )

            elif ev.type == pygame.TEXTINPUT:
                out.append(Event(type=EventType.TEXTINPUT, text=str(ev.text)))

            elif ev.type == pygame.MOUSEMOTION:
                x, y = ev.pos
                dx, dy = ev.rel
                out.append(
                    Event(
                        type=EventType.MOUSEMOTION,
                        x=int(x),
                        y=int(y),
                        dx=int(dx),
                        dy=int(dy),
                    )
                )

            elif ev.type == pygame.MOUSEBUTTONDOWN:
                # Wheel events are also mouse buttons in older pygame, but pygame2 has MOUSEWHEEL.
                out.append(
                    Event(
                        type=EventType.MOUSEBUTTONDOWN,
                        button=int(ev.button),
                        x=int(ev.pos[0]),
                        y=int(ev.pos[1]),
                    )
                )

            elif ev.type == pygame.MOUSEBUTTONUP:
                out.append(
                    Event(
                        type=EventType.MOUSEBUTTONUP,
                        button=int(ev.button),
                        x=int(ev.pos[0]),
                        y=int(ev.pos[1]),
                    )
                )

            elif ev.type == pygame.MOUSEWHEEL:
                out.append(
                    Event(
                        type=EventType.MOUSEWHEEL,
                        wheel=(int(ev.x), int(ev.y)),
                    )
                )

        return out
