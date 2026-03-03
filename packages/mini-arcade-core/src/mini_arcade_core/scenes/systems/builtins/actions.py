"""
Action-map based input bindings for scene systems.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Generic, Mapping, Protocol, TypeVar

from mini_arcade_core.backend.keys import Key
from mini_arcade_core.runtime.input_frame import ButtonState, InputFrame
from mini_arcade_core.scenes.sim_scene import BaseIntent
from mini_arcade_core.scenes.systems.base_system import BaseSystem

TContext = TypeVar("TContext")
TIntent = TypeVar("TIntent", bound=BaseIntent)


@dataclass(frozen=True)
class ActionState:
    """
    Normalized per-action state.
    """

    value: float = 0.0
    down: bool = False
    pressed: bool = False
    released: bool = False


@dataclass(frozen=True)
class ActionSnapshot:
    """
    Per-frame snapshot for all mapped actions.
    """

    _states: Mapping[str, ActionState] = field(default_factory=dict)

    def state(self, action: str) -> ActionState:
        return self._states.get(action, ActionState())

    def value(self, action: str, default: float = 0.0) -> float:
        return self._states.get(action, ActionState(value=default)).value

    def down(self, action: str) -> bool:
        return self.state(action).down

    def pressed(self, action: str) -> bool:
        return self.state(action).pressed

    def released(self, action: str) -> bool:
        return self.state(action).released


class ActionBinding(Protocol):
    """
    Strategy contract for one logical action binding.
    """

    def read(self, frame: InputFrame) -> ActionState: ...


def _button_state(frame: InputFrame, name: str) -> ButtonState:
    return frame.buttons.get(name, ButtonState(False, False, False))


@dataclass(frozen=True)
class DigitalActionBinding(ActionBinding):
    """
    Digital action sourced from keyboard and/or named buttons.
    """

    keys: tuple[Key, ...] = ()
    buttons: tuple[str, ...] = ()

    def read(self, frame: InputFrame) -> ActionState:
        key_down = any(k in frame.keys_down for k in self.keys)
        key_pressed = any(k in frame.keys_pressed for k in self.keys)
        key_released = any(k in frame.keys_released for k in self.keys)

        btn_down = any(_button_state(frame, b).down for b in self.buttons)
        btn_pressed = any(
            _button_state(frame, b).pressed for b in self.buttons
        )
        btn_released = any(
            _button_state(frame, b).released for b in self.buttons
        )

        down = key_down or btn_down
        return ActionState(
            value=1.0 if down else 0.0,
            down=down,
            pressed=key_pressed or btn_pressed,
            released=key_released or btn_released,
        )


@dataclass(frozen=True)
class AxisActionBinding(ActionBinding):
    """
    Axis action sourced from analog axes and optional digital fallbacks.
    """

    axes: tuple[str, ...] = ()
    positive_keys: tuple[Key, ...] = ()
    negative_keys: tuple[Key, ...] = ()
    positive_buttons: tuple[str, ...] = ()
    negative_buttons: tuple[str, ...] = ()
    deadzone: float = 0.15
    scale: float = 1.0

    def read(self, frame: InputFrame) -> ActionState:
        analog = 0.0
        for axis in self.axes:
            analog += float(frame.axes.get(axis, 0.0))

        pos_down = any(
            k in frame.keys_down for k in self.positive_keys
        ) or any(_button_state(frame, b).down for b in self.positive_buttons)
        neg_down = any(
            k in frame.keys_down for k in self.negative_keys
        ) or any(_button_state(frame, b).down for b in self.negative_buttons)

        digital = (1.0 if pos_down else 0.0) - (1.0 if neg_down else 0.0)
        value = (analog + digital) * self.scale
        value = max(-1.0, min(1.0, value))

        pressed = (
            any(k in frame.keys_pressed for k in self.positive_keys)
            or any(k in frame.keys_pressed for k in self.negative_keys)
            or any(
                _button_state(frame, b).pressed for b in self.positive_buttons
            )
            or any(
                _button_state(frame, b).pressed for b in self.negative_buttons
            )
        )
        released = (
            any(k in frame.keys_released for k in self.positive_keys)
            or any(k in frame.keys_released for k in self.negative_keys)
            or any(
                _button_state(frame, b).released for b in self.positive_buttons
            )
            or any(
                _button_state(frame, b).released for b in self.negative_buttons
            )
        )
        down = abs(value) > self.deadzone or pos_down or neg_down
        return ActionState(
            value=value,
            down=down,
            pressed=pressed,
            released=released,
        )


@dataclass(frozen=True)
class ActionMap:
    """
    Mapping of action IDs to concrete binding strategies.
    """

    bindings: Mapping[str, ActionBinding] = field(default_factory=dict)

    def read(self, frame: InputFrame) -> ActionSnapshot:
        states = {
            name: binding.read(frame)
            for name, binding in self.bindings.items()
        }
        return ActionSnapshot(states)


@dataclass
class ActionIntentSystem(BaseSystem[TContext], Generic[TContext, TIntent]):
    """
    Input system that converts an ActionMap snapshot into scene intent.
    """

    action_map: ActionMap
    intent_factory: Callable[[ActionSnapshot, TContext], TIntent]
    name: str = "action_intent"
    order: int = 10

    def step(self, ctx: TContext) -> None:
        frame = getattr(ctx, "input_frame", None)
        if frame is None:
            return
        snapshot = self.action_map.read(frame)
        setattr(ctx, "intent", self.intent_factory(snapshot, ctx))
