"""
Screen-space post effects base classes and protocols.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from mini_arcade_core.backend import Backend
from mini_arcade_core.engine.render.context import RenderContext


@runtime_checkable
class Effect(Protocol):
    """
    Screen-space post effect.

    IMPORTANT: Effects should draw ONLY using ctx.viewport (screen-space),
    and must not assume anything about world-space transforms.
    """

    effect_id: str

    def apply(self, backend: Backend, ctx: RenderContext):
        """
        Apply the effect to the current framebuffer.

        :param backend: Backend to use for rendering.
        :type backend: Backend

        :param ctx: Render context with viewport info.
        :type ctx: RenderContext
        """


@dataclass
class EffectParams:
    """
    Shared params (Material-ish controls) for v1.

    :ivar intensity (float): Effect intensity.
    :ivar wobble_speed (float): Speed factor for animated distortion.
    :ivar tint (tuple[int, int, int, int] | None): Optional RGBA tint.
    """

    intensity: float = 1.0
    wobble_speed: float = 1.0
    tint: tuple[int, int, int, int] | None = None


@dataclass
class EffectStack:
    """
    Runtime state: what effects are enabled + their params.

    Zero-overhead path:
        - if enabled=False OR active is empty => PostFXPass returns immediately.

    :ivar enabled (bool): Master toggle for post effects.
    :ivar active (list[str]): List of active effect IDs.
    :ivar params (dict[str, EffectParams]): Per-effect parameters.
    """

    enabled: bool = False
    active: list[str] = field(default_factory=list)
    params: dict[str, EffectParams] = field(default_factory=dict)

    def is_active(self) -> bool:
        """
        Check if any effects are active.

        :return: True if effects are enabled and at least one is active.
        :rtype: bool
        """
        return self.enabled and bool(self.active)

    def toggle(self, effect_id: str):
        """
        Toggle an effect on/off.

        :param effect_id: ID of the effect to toggle.
        :type effect_id: str
        """
        if effect_id in self.active:
            self.active.remove(effect_id)
        else:
            self.active.append(effect_id)
