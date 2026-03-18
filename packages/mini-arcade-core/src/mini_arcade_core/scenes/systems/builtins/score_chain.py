"""
Reusable helpers for short-lived score-chain windows.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

from mini_arcade_core.scenes.systems.phases import SystemPhase

# pylint: disable=invalid-name
TCtx = TypeVar("TCtx")
# pylint: enable=invalid-name


def _default_enabled_when(_ctx: object) -> bool:
    return True


@dataclass
class ScoreChainState:
    """
    Mutable chain state for consecutive score events.
    """

    step_index: int = 0
    remaining_seconds: float = 0.0

    @property
    def active(self) -> bool:
        """
        Whether the score chain is currently active and can be extended.

        :return: True if the chain is active, False otherwise.
        :rtype: bool
        """
        return self.step_index > 0 and self.remaining_seconds > 0.0


def reset_score_chain(state: ScoreChainState) -> None:
    """
    Clear the current score chain.
    """

    state.step_index = 0
    state.remaining_seconds = 0.0


def claim_score_chain_points(
    state: ScoreChainState,
    *,
    steps: tuple[int, ...],
    window_seconds: float,
) -> int:
    """
    Claim the next score value in a chain and refresh its timer.
    """

    if not steps:
        return 0

    points = steps[min(state.step_index, len(steps) - 1)]
    state.step_index += 1
    state.remaining_seconds = max(0.0, float(window_seconds))
    return int(points)


@dataclass(frozen=True)
class ScoreChainBinding(Generic[TCtx]):
    """
    Declarative score-chain expiry rule.
    """

    state_getter: Callable[[TCtx], ScoreChainState]
    on_expired: Callable[[TCtx, ScoreChainState], None] | None = None


@dataclass
class ScoreChainSystem(Generic[TCtx]):
    """
    Expire score chains after their timer runs out.
    """

    name: str = "common_score_chain"
    phase: int = SystemPhase.SIMULATION
    order: int = 17
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    bindings: tuple[ScoreChainBinding[TCtx], ...] = ()

    def step(self, ctx: TCtx) -> None:
        """Advance active score-chain timers by frame dt."""

        if not self.enabled_when(ctx):
            return

        dt = max(0.0, float(getattr(ctx, "dt", 0.0)))
        if dt <= 0.0:
            return

        for binding in self.bindings:
            state = binding.state_getter(ctx)
            if state.remaining_seconds <= 0.0:
                continue

            state.remaining_seconds = max(
                0.0,
                float(state.remaining_seconds) - dt,
            )
            if state.remaining_seconds > 0.0:
                continue

            if binding.on_expired is not None:
                binding.on_expired(ctx, state)
            reset_score_chain(state)


__all__ = [
    "ScoreChainBinding",
    "ScoreChainState",
    "ScoreChainSystem",
    "claim_score_chain_points",
    "reset_score_chain",
]
