"""
Reusable pause trigger system driven by intent.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

from mini_arcade_core.scenes.systems.base_system import BaseSystem
from mini_arcade_core.scenes.systems.phases import SystemPhase

# pylint: disable=invalid-name
TContext = TypeVar("TContext")
# pylint: enable=invalid-name


@dataclass
class IntentPauseSystem(BaseSystem[TContext], Generic[TContext]):
    """
    Generic pause trigger:
    - checks `ctx.intent.<intent_attr>`
    - optionally runs a local pause callback
    - pushes the pause command into `ctx.commands`
    """

    pause_command_factory: Callable[[TContext], object]
    name: str = "pause_intent"
    phase: int = SystemPhase.CONTROL
    order: int = 12
    intent_attr: str = "pause"
    is_already_paused: Callable[[TContext], bool] | None = None
    on_pause: Callable[[TContext], None] | None = None

    def step(self, ctx: TContext) -> None:
        intent = getattr(ctx, "intent", None)
        if intent is None:
            return

        if not bool(getattr(intent, self.intent_attr, False)):
            return

        if self.is_already_paused and self.is_already_paused(ctx):
            return

        if self.on_pause is not None:
            self.on_pause(ctx)

        ctx.commands.push(self.pause_command_factory(ctx))
