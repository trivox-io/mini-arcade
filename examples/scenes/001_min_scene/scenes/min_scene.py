"""
Minimal scene example.
"""

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade.utils.logging import logger  # type: ignore[import-not-found]
from mini_arcade_core.runtime.context import (
    RuntimeContext,  # type: ignore[import-not-found]
)
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.autoreg import (
    register_scene,  # type: ignore[import-not-found]
)
from mini_arcade_core.scenes.sim_scene import (  # type: ignore[import-not-found]
    BaseIntent,
    BaseTickContext,
    BaseWorld,
    SimScene,
)
from mini_arcade_core.scenes.systems.system_pipeline import SystemPipeline


@dataclass
class MinWorld(BaseWorld):
    """Minimal world state for our example scene."""


@dataclass(frozen=True)
class MinIntent(BaseIntent):
    """Minimal intent for our example scene."""


@dataclass
class MinTickContext(BaseTickContext[MinWorld, MinIntent]):
    """
    Context for a Min scene tick.
    """


@register_scene("min")
class MinScene(SimScene[MinTickContext, MinWorld]):
    """
    Minimal scene:
    """

    tick_context_type = MinTickContext

    def on_enter(self) -> None:
        self.world = MinWorld()

    def tick(self, input_frame: InputFrame, dt: float) -> None:  # type: ignore[override]
        # dt: your engine likely provides dt seconds. If not, approximate.
        logger.info("tick")
