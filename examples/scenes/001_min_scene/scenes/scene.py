"""
Minimal scene example.
"""

from __future__ import annotations

from mini_arcade.utils.logging import logger  # type: ignore[import-not-found]
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.autoreg import (
    register_scene,  # type: ignore[import-not-found]
)
from mini_arcade_core.scenes.sim_scene import (  # type: ignore[import-not-found]
    SimScene,
)

from .models import MinTickContext, MinWorld


@register_scene("min")
class MinScene(SimScene[MinTickContext, MinWorld]):
    """
    Minimal scene:
    """

    tick_context_type = MinTickContext

    def on_enter(self) -> None:
        self.world = MinWorld(entities=[])

    def tick(self, input_frame: InputFrame, dt: float) -> None:  # type: ignore[override]
        # dt: your engine likely provides dt seconds. If not, approximate.
        logger.info("tick")
