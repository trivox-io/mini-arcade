from __future__ import annotations

from mini_arcade_core.backend.events import Event, EventType
from mini_arcade_core.runtime.input.input_adapter import InputAdapter


def test_input_adapter_maps_mouse_button_events_to_buttons() -> None:
    adapter = InputAdapter()

    pressed = adapter.build(
        [
            Event(type=EventType.MOUSEBUTTONDOWN, button=1, x=10, y=20),
            Event(type=EventType.MOUSEBUTTONDOWN, button=3, x=30, y=40),
        ],
        frame_index=1,
        dt=1.0 / 60.0,
    )

    assert pressed.mouse_pos == (30, 40)
    assert pressed.buttons["mouse_left"].pressed is True
    assert pressed.buttons["mouse_left"].down is True
    assert pressed.buttons["mouse_right"].pressed is True
    assert pressed.buttons["mouse_right"].down is True

    released = adapter.build(
        [
            Event(type=EventType.MOUSEBUTTONUP, button=1, x=30, y=40),
            Event(type=EventType.MOUSEBUTTONUP, button=3, x=30, y=40),
        ],
        frame_index=2,
        dt=1.0 / 60.0,
    )

    assert released.buttons["mouse_left"].released is True
    assert released.buttons["mouse_left"].down is False
    assert released.buttons["mouse_right"].released is True
    assert released.buttons["mouse_right"].down is False
