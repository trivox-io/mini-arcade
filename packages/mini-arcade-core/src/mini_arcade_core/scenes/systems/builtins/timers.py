"""
Reusable timed-state helpers for temporary gameplay states.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar

from mini_arcade_core.scenes.systems.phases import SystemPhase

# pylint: disable=invalid-name
TCtx = TypeVar("TCtx")
# pylint: enable=invalid-name


def _default_enabled_when(_ctx: object) -> bool:
    return True


@dataclass
class TimedState:
    """
    Mutable state for one temporary status window.
    """

    active: bool = False
    remaining_seconds: float = 0.0
    tag: str = ""
    payload: Any = None


def activate_timed_state(
    state: TimedState,
    *,
    duration_seconds: float,
    tag: str = "",
    payload: Any = None,
) -> None:
    """
    Activate a timed state and reset its countdown.
    """

    state.active = True
    state.remaining_seconds = max(0.0, float(duration_seconds))
    state.tag = str(tag)
    state.payload = payload


def clear_timed_state(state: TimedState) -> None:
    """
    Clear a timed state immediately.
    """

    state.active = False
    state.remaining_seconds = 0.0
    state.tag = ""
    state.payload = None


@dataclass(frozen=True)
class TimedStateBinding(Generic[TCtx]):
    """
    Declarative timed-state decay rule.
    """

    state_getter: Callable[[TCtx], TimedState]
    on_expired: Callable[[TCtx, TimedState], None] | None = None


@dataclass
class TimedStateSystem(Generic[TCtx]):
    """
    Decay active timed states using frame dt.
    """

    name: str = "common_timed_state"
    phase: int = SystemPhase.SIMULATION
    order: int = 16
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    bindings: tuple[TimedStateBinding[TCtx], ...] = ()

    def step(self, ctx: TCtx) -> None:
        """Advance active timed states by the current frame delta."""

        if not self.enabled_when(ctx):
            return

        dt = max(0.0, float(getattr(ctx, "dt", 0.0)))
        if dt <= 0.0:
            return

        for binding in self.bindings:
            state = binding.state_getter(ctx)
            if not state.active:
                continue

            state.remaining_seconds = max(
                0.0,
                float(state.remaining_seconds) - dt,
            )
            if state.remaining_seconds > 0.0:
                continue

            if binding.on_expired is not None:
                binding.on_expired(ctx, state)
            clear_timed_state(state)


__all__ = [
    "TimedState",
    "TimedStateBinding",
    "TimedStateSystem",
    "activate_timed_state",
    "clear_timed_state",
]
