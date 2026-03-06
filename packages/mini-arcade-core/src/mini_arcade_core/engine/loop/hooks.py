"""
Engine loop hooks module.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Protocol

from mini_arcade_core.backend.events import Event, EventType
from mini_arcade_core.backend.keys import Key
from mini_arcade_core.engine.commands import (
    ToggleDebugOverlayCommand,
    ToggleEffectCommand,
)
from mini_arcade_core.engine.render.effects.base import EffectStack
from mini_arcade_core.utils import logger

if TYPE_CHECKING:
    from mini_arcade_core.engine.game import Engine


class LoopHooks(Protocol):
    """
    Protocol for custom loop hooks to handle events.
    """

    def on_events(self, events: Iterable[object]):
        """
        Docstring for on_events

        :param events: Iterable of input events.
        :type events: Iterable[object]
        """


class DefaultGameHooks:
    """
    Default implementation of LoopHooks for handling common events.

    :param game: The Engine instance.
    :type game: Engine
    :param effects_stack: The EffectStack for post-processing effects.
    :type effects_stack: EffectStack
    """

    def __init__(self, game: "Engine", effects_stack: EffectStack):
        self.game = game
        self.effects_stack = effects_stack

    def on_events(self, events: Iterable[Event]):
        """
        Handle common events such as window resize and debug toggles.

        :param events: Iterable of input events.
        :type events: Iterable[Event]
        """
        for e in events:
            if e.type == EventType.WINDOWRESIZED and e.size:
                w, h = e.size
                logger.debug(f"Window resized event: {w}x{h}")
                self.game.services.window.on_window_resized(w, h)

            if e.type == EventType.KEYDOWN:
                if e.key == Key.F1:
                    self.game.managers.command_queue.push(
                        ToggleDebugOverlayCommand()
                    )
                elif e.key == Key.F2:
                    self.game.managers.command_queue.push(
                        ToggleEffectCommand("crt")
                    )
                elif e.key == Key.F3:
                    self.game.managers.command_queue.push(
                        ToggleEffectCommand("vignette_noise")
                    )
                elif e.key == Key.F4:
                    self.effects_stack.enabled = not self.effects_stack.enabled
