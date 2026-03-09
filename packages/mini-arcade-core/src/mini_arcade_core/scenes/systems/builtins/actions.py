"""
Action-map based input bindings for scene systems.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    Mapping,
    Protocol,
    TypeVar,
)

from mini_arcade_core.backend.keys import Key
from mini_arcade_core.runtime.input_frame import ButtonState, InputFrame
from mini_arcade_core.scenes.systems.base_system import BaseSystem
from mini_arcade_core.scenes.systems.phases import SystemPhase

if TYPE_CHECKING:
    from mini_arcade_core.scenes.sim_scene import BaseIntent
else:
    BaseIntent = object

# pylint: disable=invalid-name
TContext = TypeVar("TContext")
TIntent = TypeVar("TIntent", bound=BaseIntent)
# pylint: enable=invalid-name


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
        """
        Get the ActionState for the given action, or a default if not found.

        :param action: The name of the action to get the state for.
        :type action: str
        :return: The ActionState for the given action, or a default if not found.
        :rtype: ActionState
        """
        return self._states.get(action, ActionState())

    def value(self, action: str, default: float = 0.0) -> float:
        """
        Get the normalized value of the action, or a default if not found.

        :param action: The name of the action to get the value for.
        :type action: str
        :param default: The default value to return if the action is not found (default 0.0).
        :type default: float
        :return: The normalized value of the action, or the default if not found.
        :rtype: float
        """
        return self._states.get(action, ActionState(value=default)).value

    def down(self, action: str) -> bool:
        """
        Check if the action is currently held down.

        :param action: The name of the action to check.
        :type action: str
        :return: True if the action is currently held down, False otherwise.
        :rtype: bool
        """
        return self.state(action).down

    def pressed(self, action: str) -> bool:
        """
        Check if the action was pressed this frame.

        :param action: The name of the action to check.
        :type action: str
        :return: True if the action was pressed this frame, False otherwise.
        :rtype: bool
        """
        return self.state(action).pressed

    def released(self, action: str) -> bool:
        """
        Check if the action was released this frame.

        :param action: The name of the action to check.
        :type action: str
        :return: True if the action was released this frame, False otherwise.
        :rtype: bool
        """
        return self.state(action).released


class ActionBinding(Protocol):
    """
    Strategy contract for one logical action binding.
    """

    def read(self, frame: InputFrame) -> ActionState:
        """
        Read the current state of this action from the input frame.

        :param frame: The input frame containing raw input states.
        :type frame: InputFrame
        :return: The current ActionState for this binding.
        :rtype: ActionState
        """


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
        """
        Read the current state of all actions from the input frame.

        :param frame: The input frame containing raw input states.
        :type frame: InputFrame
        :return: An ActionSnapshot containing the state of all actions.
        :rtype: ActionSnapshot
        """
        states = {
            name: binding.read(frame)
            for name, binding in self.bindings.items()
        }
        return ActionSnapshot(states)


def _to_str_seq(value: object) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(str(item) for item in value if isinstance(item, str))


def _to_key_seq(value: object) -> tuple[Key, ...]:
    keys: list[Key] = []
    for name in _to_str_seq(value):
        normalized = name.strip().upper()
        if not normalized:
            continue
        try:
            keys.append(Key[normalized])
        except KeyError:
            continue
    return tuple(keys)


def action_map_from_bindings_config(
    bindings: Mapping[str, Any] | None,
) -> ActionMap:
    """
    Build an ActionMap from YAML-friendly binding dictionaries.

    Supported entry formats per action:
    - digital:
        type: digital
        keys: [ESCAPE]
        buttons: [pad_start]
    - axis:
        type: axis
        axes: [left_y]
        positive_keys: [S]
        negative_keys: [W]
        positive_buttons: [pad_down]
        negative_buttons: [pad_up]
        deadzone: 0.15
        scale: 1.0
    """
    if not isinstance(bindings, Mapping):
        return ActionMap()

    parsed: dict[str, ActionBinding] = {}
    for action_name, raw_cfg in bindings.items():
        if not isinstance(action_name, str) or not isinstance(
            raw_cfg, Mapping
        ):
            continue

        kind = str(raw_cfg.get("type", "")).strip().lower()
        has_axis_shape = any(
            key in raw_cfg
            for key in (
                "axes",
                "positive_keys",
                "negative_keys",
                "positive_buttons",
                "negative_buttons",
            )
        )
        if not kind:
            kind = "axis" if has_axis_shape else "digital"

        if kind == "axis":
            parsed[action_name] = AxisActionBinding(
                axes=_to_str_seq(raw_cfg.get("axes")),
                positive_keys=_to_key_seq(raw_cfg.get("positive_keys")),
                negative_keys=_to_key_seq(raw_cfg.get("negative_keys")),
                positive_buttons=_to_str_seq(raw_cfg.get("positive_buttons")),
                negative_buttons=_to_str_seq(raw_cfg.get("negative_buttons")),
                deadzone=float(raw_cfg.get("deadzone", 0.15)),
                scale=float(raw_cfg.get("scale", 1.0)),
            )
            continue

        parsed[action_name] = DigitalActionBinding(
            keys=_to_key_seq(raw_cfg.get("keys")),
            buttons=_to_str_seq(raw_cfg.get("buttons")),
        )

    return ActionMap(bindings=parsed)


def action_map_from_controls_config(
    controls_cfg: Mapping[str, Any] | None,
    *,
    scene_key: str,
    default_action_map: ActionMap,
) -> ActionMap:
    """
    Resolve one scene ActionMap from gameplay.controls config.

    Expected layout:
      gameplay:
        controls:
          <scene_key>:
            bindings: {...}
    """
    if not isinstance(controls_cfg, Mapping):
        return default_action_map

    scene_cfg = controls_cfg.get(scene_key)
    if not isinstance(scene_cfg, Mapping):
        return default_action_map

    parsed = action_map_from_bindings_config(scene_cfg.get("bindings"))
    if parsed.bindings:
        return parsed
    return default_action_map


@dataclass
class ActionIntentSystem(BaseSystem[TContext], Generic[TContext, TIntent]):
    """
    Input system that converts an ActionMap snapshot into scene intent.
    """

    action_map: ActionMap
    intent_factory: Callable[[ActionSnapshot, TContext], TIntent]
    name: str = "action_intent"
    phase: int = SystemPhase.INPUT
    order: int = 10
    channel: str | None = None
    write_to_ctx_intent: bool = True

    def step(self, ctx: TContext) -> None:
        frame = getattr(ctx, "input_frame", None)
        if frame is None:
            return
        snapshot = self.action_map.read(frame)
        intent = self.intent_factory(snapshot, ctx)

        if self.channel:
            channels = getattr(ctx, "intent_channels", None)
            if channels is None:
                channels = {}
                setattr(ctx, "intent_channels", channels)
            channels[self.channel] = intent

        if self.write_to_ctx_intent:
            setattr(ctx, "intent", intent)


class ConfiguredActionIntentSystem(
    ActionIntentSystem[TContext, TIntent], Generic[TContext, TIntent]
):
    """
    Action-intent system configured directly from gameplay.controls settings.
    """

    def __init__(
        self,
        *,
        controls: Mapping[str, Any] | None,
        scene_key: str,
        intent_factory: Callable[[ActionSnapshot, TContext], TIntent],
        fallback_bindings: Mapping[str, Any] | None = None,
        name: str = "action_intent",
        phase: int = SystemPhase.INPUT,
        order: int = 10,
        channel: str | None = None,
        write_to_ctx_intent: bool = True,
    ):
        action_map = action_map_from_controls_config(
            controls,
            scene_key=scene_key,
            default_action_map=ActionMap(),
        )
        if not action_map.bindings and fallback_bindings is not None:
            action_map = action_map_from_bindings_config(fallback_bindings)

        if not action_map.bindings:
            raise ValueError(
                "No action bindings configured for "
                f"scene_key={scene_key!r}. "
                "Add gameplay.controls.<scene_key>.bindings to settings "
                "or provide fallback_bindings."
            )

        super().__init__(
            action_map=action_map,
            intent_factory=intent_factory,
            name=name,
            phase=phase,
            order=order,
            channel=channel,
            write_to_ctx_intent=write_to_ctx_intent,
        )
