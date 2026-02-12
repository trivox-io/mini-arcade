"""
Cheats module for Mini Arcade Core.
Provides cheat codes and related functionality.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Deque, Dict, Optional, Sequence, TypeVar

from mini_arcade_core.engine.commands import Command, CommandQueue
from mini_arcade_core.runtime.input_frame import InputFrame

# Justification: We want to keep the type variable name simple here.
# pylint: disable=invalid-name
TContext = TypeVar("TContext")
# pylint: enable=invalid-name


@dataclass(frozen=True)
class CheatCode:
    """
    Represents a registered cheat code.

    :ivar name (str): Unique name of the cheat code.
    :ivar sequence (tuple[str, ...]): Sequence of key strings that trigger the cheat.
    :ivar action (CheatAction): BaseCheatCommand to call when the cheat is activated.
    :ivar clear_buffer_on_match (bool): Whether to clear the input buffer after a match.
    :ivar enabled (bool): Whether the cheat code is enabled.
    """

    name: str
    sequence: tuple[str, ...]
    command_factory: Optional[Callable[[TContext], Command]] = None
    clear_buffer_on_match: bool = False
    enabled: bool = True


@dataclass
class CheatManager:
    """
    Reusable cheat code matcher.
    Keeps a rolling buffer of recent keys and triggers callbacks on sequence match.
    """

    buffer_size: int = 16
    enabled: bool = True
    _buffer: Deque[str] = field(default_factory=lambda: deque(maxlen=16))
    _codes: Dict[str, CheatCode[TContext]] = field(default_factory=dict)

    def __post_init__(self):
        # ensure deque maxlen matches buffer_size
        self._buffer = deque(maxlen=self.buffer_size)

    # TODO: ISolve too-many-arguments warning later
    # Justification: The method needs multiple optional parameters for flexibility.
    # pylint: disable=too-many-arguments
    def register(
        self,
        name: str,
        *,
        sequence: Sequence[str],
        command_factory: Callable[[TContext], Command],
        clear_buffer_on_match: bool = False,
        enabled: bool = True,
    ):
        """
        Register a new cheat code.

        :param name: Unique name of the cheat code.
        :type name: str

        :param sequence: Sequence of key strings that trigger the cheat.
        :type sequence: Sequence[str]

        :param command_factory: Factory function to create the Command when the cheat is activated.
        :type command_factory: Callable[[TContext], Command]

        :param clear_buffer_on_match: Whether to clear the input buffer after a match.
        :type clear_buffer_on_match: bool

        :param enabled: Whether the cheat code is enabled.
        :type enabled: bool

        :raises ValueError: If name is empty or sequence is empty.
        """
        if not name:
            raise ValueError("Cheat name must be non-empty.")
        if not sequence:
            raise ValueError(f"Cheat '{name}' sequence must be non-empty.")

        norm_seq = tuple(self._norm(s) for s in sequence)
        self._codes[name] = CheatCode(
            name=name,
            sequence=norm_seq,
            command_factory=command_factory,
            clear_buffer_on_match=clear_buffer_on_match,
            enabled=enabled,
        )

    # pylint: enable=too-many-arguments

    def process_frame(
        self,
        input_frame: InputFrame,
        *,
        context: TContext,
        queue: CommandQueue,
    ) -> list[str]:
        """
        Process an InputFrame for cheat code matches.

        :param input_frame: InputFrame containing current inputs.
        :type input_frame: InputFrame

        :param context: Context to pass to command factories.
        :type context: TContext

        :param queue: CommandQueue to push matched commands into.
        :type queue: CommandQueue

        :return: List of names of matched cheat codes.
        :rtype: list[str]
        """
        if not self.enabled:
            return []

        matched: list[str] = []
        for key in input_frame.keys_pressed:
            key_name = getattr(key, "name", str(key))
            matched.extend(
                self.process_key(key_name, context=context, queue=queue)
            )
        return matched

    def process_key(
        self, key: str, *, context: TContext, queue: CommandQueue
    ) -> list[str]:
        """
        Process a single key input.

        :param key: The key string to process.
        :type key: str

        :param context: Context to pass to command factories.
        :type context: TContext

        :param queue: CommandQueue to push matched commands into.
        :type queue: CommandQueue

        :return: List of names of matched cheat codes.
        :rtype: list[str]
        """
        if not self.enabled:
            return []

        k = self._norm(key)
        if not k:
            return []

        self._buffer.append(k)
        buf = tuple(self._buffer)

        matched: list[str] = []
        for code in self._codes.values():
            if not code.enabled:
                continue

            seq = code.sequence
            if len(seq) > len(buf):
                continue

            if buf[-len(seq) :] == seq:
                queue.push(code.command_factory(context))
                matched.append(code.name)

                if code.clear_buffer_on_match:
                    self._buffer.clear()
                    break

        return matched

    @staticmethod
    def _norm(s: str) -> str:
        return s.strip().upper()
