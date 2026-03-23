# Knockout Brackets Internals

## Purpose

This page documents the reusable single-elimination bracket helpers added to
Mini Arcade for tournament-style simulations.

The target use case is broader than sports brackets:

- autonomous ball-vs-ball tournaments
- country / food / celebrity "coup" simulations
- any scenario where named contestants are seeded, paired, and advanced through
  a knockout tree

## Core building blocks

Implementation:
`packages/mini-arcade-core/src/mini_arcade_core/scenes/systems/builtins/brackets.py`

Main types:

- `ContestantProfile`
  generic identity + presentation model (`id`, `name`, optional
  `portrait_path`, optional `portrait_texture`, badge colors, payload)
- `KnockoutBracketState`
  mutable bracket state (contestants, rounds, champion)
- `KnockoutMatchState`
  one match slot in the tree
- `KnockoutMatchResult`
  one resolved winner payload

Main helpers:

- `seed_knockout_bracket(...)`
- `claim_knockout_match_winner(...)`
- `playable_knockout_matches(...)`
- `build_knockout_layout(...)`

Main systems:

- `KnockoutBracketSeedSystem`
- `KnockoutBracketProgressSystem`

## Design intent

The bracket logic is intentionally separated from simulation-specific gameplay.

The reusable layer only knows about:

- contestant profiles
- seeded entrant order
- round/match structure
- winner progression
- visual layout positions for bracket rendering

It does **not** assume:

- sports-specific rules
- score formatting
- how a match winner is decided
- how portraits are loaded

That makes the same bracket usable by:

- a system lab
- a UI-only simulation
- a full game where each matchup launches a battle scene

## Portraits and names

`ContestantProfile` supports both:

- `portrait_path`
- `portrait_texture`

Recommended pattern:

1. keep image paths in settings/config data
2. resolve them during scene/bootstrap setup with the backend texture loader
3. store the resolved texture id on `portrait_texture`
4. keep `name` and `badge_text` as the safe fallback for labs or missing assets

This mirrors the same config-to-runtime texture resolution pattern used in
games like Space Invaders.

## Layout helper

`build_knockout_layout(...)` computes deterministic card positions and
connector anchors for each round.

That helper exists so render code can stay simple:

- systems ask for the bracket layout
- renderers draw cards, names, badges, portraits, and connector lines
- game-specific UIs can change styling without re-implementing bracket geometry

## System lab references

Reference experiments:

- `experiments/knockout_bracket_seed_lab/system_lab_case.py`
- `experiments/knockout_bracket_progress_lab/system_lab_case.py`

These labs validate:

- shuffling 16 entrants into a bracket
- rendering names + avatar/badge slots
- selecting winners and advancing them round by round
- keeping the system generic enough for future `Ball vs Ball` integration
