"""
Reusable intent-driven command dispatch system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Generic, Mapping, TypeVar

from mini_arcade_core.scenes.systems.base_system import BaseSystem
from mini_arcade_core.scenes.systems.phases import SystemPhase

# pylint: disable=invalid-name
TContext = TypeVar("TContext")
# pylint: enable=invalid-name


@dataclass
class IntentCommandSystem(BaseSystem[TContext], Generic[TContext]):
    """
    Push commands when configured intent attributes are truthy for this tick.
    """

    bindings: Mapping[str, Callable[[TContext], object]] = field(
        default_factory=dict
    )
    name: str = "intent_commands"
    phase: int = SystemPhase.CONTROL
    order: int = 13
    intent_attr: str = "intent"

    def step(self, ctx: TContext) -> None:
        intent = getattr(ctx, self.intent_attr, None)
        commands = getattr(ctx, "commands", None)
        if intent is None or commands is None:
            return

        for intent_field, command_factory in self.bindings.items():
            if not bool(getattr(intent, intent_field, False)):
                continue
            command = command_factory(ctx)
            if command is None:
                continue
            commands.push(command)
