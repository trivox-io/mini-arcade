"""
Screen-space post effects registry.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from mini_arcade_core.engine.render.effects.base import Effect


@dataclass
class EffectRegistry:
    """
    Registry of available screen-space post effects.

    :ivar _effects: dict[str, Effect]: Internal mapping of effect IDs to effects.
    """

    _effects: dict[str, Effect] = field(default_factory=dict)

    def register(self, effect: Effect):
        """
        Register a new effect in the registry.

        :param effect: Effect to register.
        :type effect: Effect
        """
        self._effects[effect.effect_id] = effect

    def get(self, effect_id: str) -> Effect | None:
        """
        Get an effect by its ID.

        :param effect_id: ID of the effect to retrieve.
        :type effect_id: str

        :return: Effect instance or None if not found.
        :rtype: Effect | None
        """
        return self._effects.get(effect_id)

    def all_ids(self) -> list[str]:
        """
        Get a list of all registered effect IDs.

        :return: List of effect IDs.
        :rtype: list[str]
        """
        return list(self._effects.keys())
