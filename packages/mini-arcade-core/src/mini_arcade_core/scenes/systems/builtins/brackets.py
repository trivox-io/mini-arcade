"""
Reusable helpers for single-elimination knockout brackets.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, Iterable, Literal, TypeVar

from mini_arcade_core.scenes.systems.phases import SystemPhase
from mini_arcade_core.spaces.geometry.size import Size2D
from mini_arcade_core.spaces.math.vec2 import Vec2

# pylint: disable=invalid-name
TCtx = TypeVar("TCtx")
# pylint: enable=invalid-name


def _default_seed_trigger(_ctx: object, state: "KnockoutBracketState") -> bool:
    return not bool(state.rounds)


def _default_progress_enabled(_ctx: object) -> bool:
    return True


def _winner_initials(name: str) -> str:
    parts = [part for part in str(name).replace("-", " ").split() if part]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return f"{parts[0][0]}{parts[-1][0]}".upper()


@dataclass
class ContestantProfile:
    """
    Generic entrant identity/presentation data for simulations and brackets.
    """

    id: str
    name: str
    portrait_texture: int | None = None
    portrait_path: str | None = None
    badge_text: str | None = None
    primary_color: tuple[int, int, int] = (96, 168, 255)
    secondary_color: tuple[int, int, int] = (24, 30, 42)
    payload: dict[str, Any] = field(default_factory=dict)

    def display_badge(self) -> str:
        """Return the short badge text used when no portrait is available."""

        if self.badge_text:
            return str(self.badge_text)
        return _winner_initials(self.name)


@dataclass
class KnockoutMatchState:
    """
    Mutable state for one single-elimination match slot.
    """

    id: str
    round_index: int
    slot_index: int
    entrant_a_id: str | None = None
    entrant_b_id: str | None = None
    winner_id: str | None = None
    next_match_id: str | None = None
    next_slot: Literal["a", "b"] | None = None
    source_match_a_id: str | None = None
    source_match_b_id: str | None = None

    @property
    def playable(self) -> bool:
        """Whether both entrants exist and the winner is still unresolved."""

        return (
            self.entrant_a_id is not None
            and self.entrant_b_id is not None
            and self.winner_id is None
        )


@dataclass
class KnockoutBracketState:
    """
    Whole-bracket state shared across systems and renderers.
    """

    title: str = "Knockout Bracket"
    contestant_ids: list[str] = field(default_factory=list)
    contestants: dict[str, ContestantProfile] = field(default_factory=dict)
    rounds: list[list[KnockoutMatchState]] = field(default_factory=list)
    champion_id: str | None = None
    seed_value: int = 0


@dataclass(frozen=True)
class KnockoutMatchResult:
    """
    Declarative result payload emitted by bracket UIs or simulations.
    """

    match_id: str
    winner_id: str


@dataclass(frozen=True)
class KnockoutMatchLayout:
    """
    Layout result for one rendered knockout match card.
    """

    match_id: str
    round_index: int
    slot_index: int
    center: Vec2
    size: Size2D
    entrant_a_center: Vec2
    entrant_b_center: Vec2
    inbound_anchor_a: Vec2
    inbound_anchor_b: Vec2
    outbound_anchor: Vec2


def next_bracket_size(count: int) -> int:
    """
    Return the next power-of-two bracket size for the entrant count.
    """

    normalized = max(0, int(count))
    if normalized <= 1:
        return normalized
    return 1 << math.ceil(math.log2(normalized))


def clear_knockout_bracket(state: KnockoutBracketState) -> None:
    """
    Reset bracket rounds and champion while preserving the title.
    """

    state.contestant_ids.clear()
    state.contestants.clear()
    state.rounds.clear()
    state.champion_id = None


def _find_match(
    state: KnockoutBracketState,
    match_id: str,
) -> KnockoutMatchState | None:
    for round_matches in state.rounds:
        for match in round_matches:
            if match.id == match_id:
                return match
    return None


def build_knockout_rounds(
    contestant_ids: Iterable[str],
) -> list[list[KnockoutMatchState]]:
    """
    Build the round/match graph for a single-elimination bracket.
    """

    entrant_ids = [str(value) for value in contestant_ids if str(value)]
    if len(entrant_ids) <= 1:
        return []

    bracket_size = next_bracket_size(len(entrant_ids))
    padded = [*entrant_ids, *([None] * (bracket_size - len(entrant_ids)))]

    rounds: list[list[KnockoutMatchState]] = []
    match_count = bracket_size // 2
    round_index = 0
    while match_count >= 1:
        rounds.append(
            [
                KnockoutMatchState(
                    id=f"r{round_index + 1}m{slot_index + 1}",
                    round_index=round_index,
                    slot_index=slot_index,
                )
                for slot_index in range(match_count)
            ]
        )
        round_index += 1
        match_count //= 2

    for slot_index, match in enumerate(rounds[0]):
        match.entrant_a_id = padded[slot_index * 2]
        match.entrant_b_id = padded[(slot_index * 2) + 1]

    for round_matches, next_round in zip(rounds, rounds[1:]):
        for match in round_matches:
            next_match = next_round[match.slot_index // 2]
            match.next_match_id = next_match.id
            match.next_slot = "a" if (match.slot_index % 2 == 0) else "b"
            if match.next_slot == "a":
                next_match.source_match_a_id = match.id
            else:
                next_match.source_match_b_id = match.id

    return rounds


def _advance_winner_to_next_match(
    state: KnockoutBracketState,
    match: KnockoutMatchState,
    winner_id: str,
) -> None:
    if not match.next_match_id or not match.next_slot:
        state.champion_id = winner_id
        return

    next_match = _find_match(state, match.next_match_id)
    if next_match is None:
        state.champion_id = winner_id
        return

    if match.next_slot == "a":
        next_match.entrant_a_id = winner_id
    else:
        next_match.entrant_b_id = winner_id


def resolve_knockout_byes(state: KnockoutBracketState) -> None:
    """
    Auto-advance entrants through bye matches.
    """

    changed = True
    while changed:
        changed = False
        for round_matches in state.rounds:
            for match in round_matches:
                if match.winner_id is not None:
                    continue
                winner_id = None
                if (
                    _slot_is_true_bye(state, match, slot="b")
                    and match.entrant_a_id
                ):
                    winner_id = match.entrant_a_id
                elif (
                    _slot_is_true_bye(state, match, slot="a")
                    and match.entrant_b_id
                ):
                    winner_id = match.entrant_b_id
                if winner_id is None:
                    continue
                match.winner_id = winner_id
                _advance_winner_to_next_match(state, match, winner_id)
                changed = True


def _slot_is_true_bye(
    state: KnockoutBracketState,
    match: KnockoutMatchState,
    *,
    slot: Literal["a", "b"],
) -> bool:
    """
    Return whether one side is genuinely empty, not just unresolved.
    """

    source_match_id = (
        match.source_match_a_id if slot == "a" else match.source_match_b_id
    )
    if source_match_id is None:
        return (
            match.entrant_a_id is None
            if slot == "a"
            else match.entrant_b_id is None
        )

    source_match = _find_match(state, source_match_id)
    if source_match is None:
        return False
    return (
        source_match.winner_id is None
        and source_match.entrant_a_id is None
        and source_match.entrant_b_id is None
    )


def seed_knockout_bracket(
    state: KnockoutBracketState,
    *,
    contestants: Iterable[ContestantProfile],
    seed: int = 0,
    shuffle: bool = True,
) -> None:
    """
    Replace the bracket with a new seeded contestant order.

    :param state: The knockout bracket state to seed.
    :type state: KnockoutBracketState
    :param contestants: An iterable of contestant profiles to seed into the bracket.
    :type contestants: Iterable[ContestantProfile]
    :param seed: An optional seed value for shuffling the contestants.
    :type seed: int
    :param shuffle: Whether to shuffle the contestants before seeding.
    :type shuffle: bool
    """
    profiles = list(contestants)
    state.seed_value = int(seed)
    state.contestants = {profile.id: profile for profile in profiles}
    ordered_ids = [profile.id for profile in profiles]
    if shuffle and len(ordered_ids) > 1:
        rng = random.Random(int(seed))
        rng.shuffle(ordered_ids)
    state.contestant_ids = ordered_ids
    state.rounds = build_knockout_rounds(ordered_ids)
    state.champion_id = ordered_ids[0] if len(ordered_ids) == 1 else None
    resolve_knockout_byes(state)


def claim_knockout_match_winner(
    state: KnockoutBracketState,
    *,
    match_id: str,
    winner_id: str,
) -> bool:
    """
    Record one match winner and advance them into the next round.
    """

    match = _find_match(state, match_id)
    if match is None:
        return False
    if match.winner_id is not None:
        return False
    if winner_id not in {match.entrant_a_id, match.entrant_b_id}:
        return False

    match.winner_id = winner_id
    _advance_winner_to_next_match(state, match, winner_id)
    resolve_knockout_byes(state)
    return True


def playable_knockout_matches(
    state: KnockoutBracketState,
) -> tuple[KnockoutMatchState, ...]:
    """
    Return unresolved matches whose entrants are both present.
    """

    playable: list[KnockoutMatchState] = []
    for round_matches in state.rounds:
        for match in round_matches:
            if match.playable:
                playable.append(match)
    return tuple(playable)


def build_knockout_layout(
    state: KnockoutBracketState,
    *,
    origin: Vec2 = Vec2(180.0, 110.0),
    round_spacing: float = 230.0,
    first_round_step: float = 92.0,
    match_card_size: Size2D = Size2D(184, 64),
) -> tuple[KnockoutMatchLayout, ...]:
    """
    Build deterministic card positions for a rendered bracket view.
    """

    if not state.rounds:
        return ()

    size = Size2D(
        int(match_card_size.width),
        int(match_card_size.height),
    )
    row_offset = max(14.0, float(size.height) * 0.22)
    total_rounds = len(state.rounds)
    final_round_index = total_rounds - 1
    final_x = float(origin.x) + (final_round_index * float(round_spacing))

    layouts_by_match_id: dict[str, KnockoutMatchLayout] = {}
    left_per_round: list[list[KnockoutMatchLayout]] = []
    right_per_round: list[list[KnockoutMatchLayout]] = []

    for round_index, round_matches in enumerate(state.rounds[:-1]):
        half = len(round_matches) // 2
        distance = final_round_index - round_index
        left_x = final_x - (distance * float(round_spacing))
        right_x = final_x + (distance * float(round_spacing))
        left_round: list[KnockoutMatchLayout] = []
        right_round: list[KnockoutMatchLayout] = []

        for local_slot, match in enumerate(round_matches[:half]):
            if round_index == 0:
                y = float(origin.y) + (local_slot * float(first_round_step))
            else:
                prev = left_per_round[round_index - 1]
                upper = prev[local_slot * 2].center.y
                lower = prev[(local_slot * 2) + 1].center.y
                y = (upper + lower) * 0.5

            layout = KnockoutMatchLayout(
                match_id=match.id,
                round_index=round_index,
                slot_index=match.slot_index,
                center=Vec2(left_x, y),
                size=size,
                entrant_a_center=Vec2(left_x, y - row_offset),
                entrant_b_center=Vec2(left_x, y + row_offset),
                inbound_anchor_a=Vec2(
                    left_x - (float(size.width) * 0.5),
                    y - row_offset,
                ),
                inbound_anchor_b=Vec2(
                    left_x - (float(size.width) * 0.5),
                    y + row_offset,
                ),
                outbound_anchor=Vec2(
                    left_x + (float(size.width) * 0.5),
                    y,
                ),
            )
            left_round.append(layout)
            layouts_by_match_id[match.id] = layout

        for local_slot, match in enumerate(round_matches[half:]):
            if round_index == 0:
                y = float(origin.y) + (local_slot * float(first_round_step))
            else:
                prev = right_per_round[round_index - 1]
                upper = prev[local_slot * 2].center.y
                lower = prev[(local_slot * 2) + 1].center.y
                y = (upper + lower) * 0.5

            layout = KnockoutMatchLayout(
                match_id=match.id,
                round_index=round_index,
                slot_index=match.slot_index,
                center=Vec2(right_x, y),
                size=size,
                entrant_a_center=Vec2(right_x, y - row_offset),
                entrant_b_center=Vec2(right_x, y + row_offset),
                inbound_anchor_a=Vec2(
                    right_x + (float(size.width) * 0.5),
                    y - row_offset,
                ),
                inbound_anchor_b=Vec2(
                    right_x + (float(size.width) * 0.5),
                    y + row_offset,
                ),
                outbound_anchor=Vec2(
                    right_x - (float(size.width) * 0.5),
                    y,
                ),
            )
            right_round.append(layout)
            layouts_by_match_id[match.id] = layout

        left_per_round.append(left_round)
        right_per_round.append(right_round)

    final_match = state.rounds[-1][0]
    if left_per_round and right_per_round:
        final_y = (
            left_per_round[-1][0].center.y + right_per_round[-1][0].center.y
        ) * 0.5
    else:
        final_y = float(origin.y)
    final_layout = KnockoutMatchLayout(
        match_id=final_match.id,
        round_index=final_match.round_index,
        slot_index=final_match.slot_index,
        center=Vec2(final_x, final_y),
        size=size,
        entrant_a_center=Vec2(final_x, final_y - row_offset),
        entrant_b_center=Vec2(final_x, final_y + row_offset),
        inbound_anchor_a=Vec2(
            final_x - (float(size.width) * 0.5),
            final_y - row_offset,
        ),
        inbound_anchor_b=Vec2(
            final_x + (float(size.width) * 0.5),
            final_y + row_offset,
        ),
        outbound_anchor=Vec2(final_x, final_y),
    )
    layouts_by_match_id[final_match.id] = final_layout

    ordered_layouts: list[KnockoutMatchLayout] = []
    for round_matches in state.rounds:
        for match in round_matches:
            ordered_layouts.append(layouts_by_match_id[match.id])
    return tuple(ordered_layouts)


@dataclass(frozen=True)
class KnockoutBracketSeedBinding(Generic[TCtx]):
    """
    Declarative seeding rule for a knockout bracket.
    """

    state_getter: Callable[[TCtx], KnockoutBracketState]
    contestants_getter: Callable[[TCtx], Iterable[ContestantProfile]]
    seed_getter: Callable[[TCtx], int] | None = None
    should_seed: Callable[[TCtx, KnockoutBracketState], bool] | None = None
    shuffle: bool = True
    on_seeded: Callable[[TCtx, KnockoutBracketState], None] | None = None


@dataclass
class KnockoutBracketSeedSystem(Generic[TCtx]):
    """
    Seed/reshape one bracket from a contestant roster.
    """

    name: str = "knockout_bracket_seed"
    phase: int = SystemPhase.SIMULATION
    order: int = 12
    bindings: tuple[KnockoutBracketSeedBinding[TCtx], ...] = ()

    def step(self, ctx: TCtx) -> None:
        """
        Seed or reshape the bracket based on the current context.

        :param ctx: The system context, passed to all binding getters.
        :type ctx: TCtx
        """
        for binding in self.bindings:
            state = binding.state_getter(ctx)
            trigger = (
                binding.should_seed(ctx, state)
                if binding.should_seed is not None
                else _default_seed_trigger(ctx, state)
            )
            if not trigger:
                continue

            seed = binding.seed_getter(ctx) if binding.seed_getter else 0
            seed_knockout_bracket(
                state,
                contestants=binding.contestants_getter(ctx),
                seed=int(seed),
                shuffle=bool(binding.shuffle),
            )
            if binding.on_seeded is not None:
                binding.on_seeded(ctx, state)


@dataclass(frozen=True)
class KnockoutBracketProgressBinding(Generic[TCtx]):
    """
    Declarative result-consumption rule for a knockout bracket.
    """

    state_getter: Callable[[TCtx], KnockoutBracketState]
    result_getter: Callable[[TCtx], KnockoutMatchResult | None]
    clear_result: Callable[[TCtx], None] | None = None


@dataclass
class KnockoutBracketProgressSystem(Generic[TCtx]):
    """
    Advance brackets when one resolved match result is available.
    """

    name: str = "knockout_bracket_progress"
    phase: int = SystemPhase.SIMULATION
    order: int = 18
    enabled_when: Callable[[TCtx], bool] = _default_progress_enabled
    bindings: tuple[KnockoutBracketProgressBinding[TCtx], ...] = ()

    def step(self, ctx: TCtx) -> None:
        """
        For each binding, claim the reported match winner and clear the result.

        :param ctx: The system context, passed to all binding getters.
        :type ctx: TCtx
        """
        if not self.enabled_when(ctx):
            return

        for binding in self.bindings:
            result = binding.result_getter(ctx)
            if result is None:
                continue

            claim_knockout_match_winner(
                binding.state_getter(ctx),
                match_id=result.match_id,
                winner_id=result.winner_id,
            )
            if binding.clear_result is not None:
                binding.clear_result(ctx)


__all__ = [
    "ContestantProfile",
    "KnockoutBracketProgressBinding",
    "KnockoutBracketProgressSystem",
    "KnockoutBracketSeedBinding",
    "KnockoutBracketSeedSystem",
    "KnockoutBracketState",
    "KnockoutMatchLayout",
    "KnockoutMatchResult",
    "KnockoutMatchState",
    "build_knockout_layout",
    "build_knockout_rounds",
    "claim_knockout_match_winner",
    "clear_knockout_bracket",
    "next_bracket_size",
    "playable_knockout_matches",
    "resolve_knockout_byes",
    "seed_knockout_bracket",
]
