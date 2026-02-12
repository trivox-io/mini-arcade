"""
Input frame data structure for capturing input state per frame.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, FrozenSet, Tuple

from mini_arcade_core.backend.keys import Key


@dataclass(frozen=True)
class ButtonState:
    """
    State of a single action button.

    :ivar down (bool): Whether the button is currently held down.
    :ivar pressed (bool): Whether the button was pressed this frame.
    :ivar released (bool): Whether the button was released this frame.
    """

    down: bool
    pressed: bool
    released: bool

    def to_dict(self) -> Dict[str, bool]:
        """
        Convert the ButtonState to a dictionary.

        :return: Dictionary representation of the ButtonState.
        :rtype: Dict[str, bool]
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, bool]) -> ButtonState:
        """
        Create a ButtonState from a dictionary.

        :param data: Dictionary containing button state data.
        :type data: Dict[str, bool]

        :return: ButtonState instance.
        :rtype: ButtonState
        """
        return cls(
            down=data.get("down", False),
            pressed=data.get("pressed", False),
            released=data.get("released", False),
        )


# TODO: Solve too-many-instance-attributes warning later
# Justification: This data class needs multiple attributes to capture input state.
# pylint: disable=too-many-instance-attributes
@dataclass(frozen=True)
class InputFrame:
    """
    Snapshot of input state for a single frame.

    :ivar frame_index (int): Sequential index of the frame.
    :ivar dt (float): Delta time since the last frame in seconds.
    :ivar keys_down (FrozenSet[Key]): Set of currently held down keys.
    :ivar keys_pressed (FrozenSet[Key]): Set of keys pressed this frame.
    :ivar keys_released (FrozenSet[Key]): Set of keys released this frame.
    :ivar buttons (Dict[str, ButtonState]): Mapping of action button names to their states.
    :ivar axes (Dict[str, float]): Mapping of axis names to their float values.
    :ivar mouse_pos (Tuple[int, int]): Current mouse position (x, y).
    :ivar mouse_delta (Tuple[int, int]): Mouse movement delta (dx, dy)
    :ivar text_input (str): Text input entered this frame.
    :ivar quit (bool): Whether a quit request was made this frame.
    """

    frame_index: int
    dt: float

    # Physical keys (device-level snapshot) – supports cheats & replay
    keys_down: FrozenSet[Key] = frozenset()
    keys_pressed: FrozenSet[Key] = frozenset()
    keys_released: FrozenSet[Key] = frozenset()

    # action buttons (jump, confirm, pause, etc.)
    buttons: Dict[str, ButtonState] = field(default_factory=dict)
    # axes (move_y, aim_x, etc.)
    axes: Dict[str, float] = field(default_factory=dict)

    # optional: pass through for UI needs
    mouse_pos: Tuple[int, int] = (0, 0)
    mouse_delta: Tuple[int, int] = (0, 0)
    text_input: str = ""

    # Window/OS quit request
    quit: bool = False

    def to_dict(self) -> Dict[str, object]:
        """
        Convert the InputFrame to a dictionary.

        :return: Dictionary representation of the InputFrame.
        :rtype: Dict[str, object]
        """
        data = asdict(self)

        # Convert ButtonState objects to dicts
        data["buttons"] = {
            name: state.to_dict() for name, state in self.buttons.items()
        }

        # Convert FrozenSet to list for serialization
        data["keys_down"] = [k.value for k in self.keys_down]
        data["keys_pressed"] = [k.value for k in self.keys_pressed]
        data["keys_released"] = [k.value for k in self.keys_released]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> InputFrame:
        """
        Create an InputFrame from a dictionary.

        :param data: Dictionary containing input frame data.
        :type data: Dict[str, object]

        :return: InputFrame instance.
        :rtype: InputFrame
        """
        return cls(
            frame_index=data.get("frame_index", 0),
            dt=data.get("dt", 0.0),
            keys_down=frozenset(Key(v) for v in data.get("keys_down", [])),
            keys_pressed=frozenset(
                Key(v) for v in data.get("keys_pressed", [])
            ),
            keys_released=frozenset(
                Key(v) for v in data.get("keys_released", [])
            ),
            buttons={
                name: ButtonState.from_dict(state)
                for name, state in data.get("buttons", {}).items()
            },
            axes=data.get("axes", {}),
            mouse_pos=tuple(data.get("mouse_pos", (0, 0))),
            mouse_delta=tuple(data.get("mouse_delta", (0, 0))),
            text_input=data.get("text_input", ""),
            quit=data.get("quit", False),
        )


# pylint: enable=too-many-instance-attributes
