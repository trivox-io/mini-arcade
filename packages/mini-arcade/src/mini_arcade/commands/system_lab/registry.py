"""
Registry primitives for isolated system lab cases.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

from mini_arcade.utils.implementation_registry import ImplementationRegistry


@dataclass(frozen=True)
class SystemLabVisualSpec:
    """
    Declarative configuration for the built-in visual system lab runner.
    """

    tick_context_type: type[object]
    title: str = "System Lab"
    scene_id: str = "system_lab_visual"
    fps: int = 60
    virtual_resolution: tuple[int, int] = (800, 600)
    window_size: tuple[int, int] | None = None
    background_color: tuple[int, int, int] = (14, 14, 20)
    backend_provider: str = "pygame"
    controls_scene_key: str | None = None
    input_fallback_bindings: Mapping[str, Any] | None = None
    intent_factory: Callable[[Any, Any], object] | None = None
    gameplay_overrides: dict[str, Any] = field(default_factory=dict)
    debug_overlay_enabled: bool = True
    debug_overlay_start_visible: bool = False
    debug_overlay_title: str = "System Lab"
    debug_overlay_sections: tuple[str, ...] = (
        "timing",
        "render",
        "viewport",
        "effects",
        "stack",
        "scene",
    )
    hot_reload_enabled: bool = True
    hot_reload_key: str = "F5"
    hot_reload_poll_seconds: float = 0.5
    enable_profiler: bool = False
    enable_profiler: bool = False


class BaseSystemLabCase(ABC):
    """
    Contract for one isolated system run scenario.
    """

    visual_title: str = "System Lab"
    visual_scene_id: str = "system_lab_visual"
    visual_fps: int = 60
    visual_virtual_resolution: tuple[int, int] = (800, 600)
    visual_window_size: tuple[int, int] | None = None
    visual_background_color: tuple[int, int, int] = (14, 14, 20)
    visual_backend_provider: str = "pygame"
    visual_controls_scene_key: str | None = None
    visual_input_fallback_bindings: Mapping[str, Any] | None = None
    visual_gameplay_overrides: dict[str, Any] = {}
    visual_debug_overlay_enabled: bool = True
    visual_debug_overlay_start_visible: bool = False
    visual_debug_overlay_title: str = "System Lab"
    visual_debug_overlay_sections: tuple[str, ...] = (
        "timing",
        "render",
        "viewport",
        "effects",
        "stack",
        "scene",
    )
    visual_hot_reload_enabled: bool = True
    visual_hot_reload_key: str = "F5"
    visual_hot_reload_poll_seconds: float = 0.5
    visual_enable_profiler: bool = False

    @abstractmethod
    def build_system(self) -> object:
        """
        Build the system instance to execute.
        """

    @abstractmethod
    def build_context(self) -> object:
        """
        Build the context passed into ``system.step(ctx)``.
        """

    def before_step(
        self, *, step_index: int, system: object, ctx: object
    ) -> None:
        """
        Optional hook before each isolated step.
        """

    def after_step(
        self, *, step_index: int, system: object, ctx: object
    ) -> None:
        """
        Optional hook after each isolated step.
        """

    # Justification: This method is part of the public contract for system lab cases,
    # and may be called by external code, so it should be included in the base class
    # even if not all cases need to implement it.
    # pylint: disable=unused-argument
    def summarize(
        self,
        *,
        system: object,
        ctx: object,
        steps: int,
    ) -> dict[str, Any]:
        """
        Optional summary data appended to command output.
        """
        return {}

    # pylint: enable=unused-argument

    def run_visual(self) -> int | None:
        """
        Optional interactive runner for visual/system-driven lab cases.

        Return ``None`` to let the processor fall back to the built-in reusable
        visual lab runner driven by ``build_visual_spec()``.
        """
        return None

    def build_visual_spec(self) -> SystemLabVisualSpec | None:
        """
        Build the visual runner specification for this case.

        The default implementation reuses the context type returned by
        ``build_context()`` and the visual class attributes declared on the
        case, which keeps simple experiments down to one file.
        """
        ctx = self.build_context()
        if not hasattr(ctx, "world"):
            return None

        return SystemLabVisualSpec(
            tick_context_type=ctx.__class__,
            title=self.visual_title,
            scene_id=self.visual_scene_id,
            fps=int(self.visual_fps),
            virtual_resolution=tuple(
                int(value) for value in self.visual_virtual_resolution
            ),
            window_size=(
                None
                if self.visual_window_size is None
                else tuple(int(value) for value in self.visual_window_size)
            ),
            background_color=tuple(
                int(value) for value in self.visual_background_color
            ),
            backend_provider=str(self.visual_backend_provider),
            controls_scene_key=self.visual_controls_scene_key,
            input_fallback_bindings=self.visual_input_fallback_bindings,
            intent_factory=self.build_visual_intent,
            gameplay_overrides=dict(self.visual_gameplay_overrides),
            debug_overlay_enabled=bool(self.visual_debug_overlay_enabled),
            debug_overlay_start_visible=bool(
                self.visual_debug_overlay_start_visible
            ),
            debug_overlay_title=self.visual_debug_overlay_title,
            debug_overlay_sections=tuple(self.visual_debug_overlay_sections),
            hot_reload_enabled=bool(self.visual_hot_reload_enabled),
            hot_reload_key=str(self.visual_hot_reload_key),
            hot_reload_poll_seconds=float(self.visual_hot_reload_poll_seconds),
            enable_profiler=bool(self.visual_enable_profiler),
        )

    def build_visual_world(
        self,
        *,
        viewport: tuple[float, float],
    ) -> object:
        """
        Build the world used by the built-in visual runner.

        By default this reuses ``build_context().world`` and updates a
        ``viewport`` attribute if the world defines one.
        """
        ctx = self.build_context()
        if not hasattr(ctx, "world"):
            raise RuntimeError(
                "Visual system lab requires build_context() to return an "
                "object with a 'world' attribute, or build_visual_world() "
                "must be overridden."
            )
        world = getattr(ctx, "world")
        if hasattr(world, "viewport"):
            setattr(
                world, "viewport", (float(viewport[0]), float(viewport[1]))
            )
        return world

    def build_visual_systems(self) -> tuple[object, ...]:
        """
        Build the systems installed into the built-in visual runner scene.
        """
        return (self.build_system(),)

    # pylint: disable=unused-argument
    def build_visual_intent(self, actions: Any, ctx: Any) -> object | None:
        """
        Optional action-snapshot to intent adapter for the visual runner.
        """
        return None

    def visual_debug_lines(self, *, world: object) -> list[str]:
        """
        Optional debug overlay lines exposed by the built-in visual runner.
        """
        return []

    # pylint: enable=unused-argument


class SystemLabRegistry(ImplementationRegistry[BaseSystemLabCase]):
    """
    Registry of named isolated system cases.
    """


SystemLabRegistry.implementation_base = BaseSystemLabCase


__all__ = [
    "BaseSystemLabCase",
    "SystemLabRegistry",
    "SystemLabVisualSpec",
]
