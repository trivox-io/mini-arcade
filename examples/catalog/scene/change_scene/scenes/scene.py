"""
Scenes for scene/change_scene tutorial example.
"""

from __future__ import annotations

import itertools
import math

from mini_arcade_core.backend.backend import Backend
from mini_arcade_core.backend.keys import Key
from mini_arcade_core.engine.commands import ChangeSceneCommand
from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.sim_scene import SimScene

SCENE_HUB = "change_scene_hub"
SCENE_ARENA = "change_scene_arena"
SCENE_LAB = "change_scene_lab"

_INSTANCE_SEQ = itertools.count(1)


# Justification: This scene overrides tick directly and does not use a tick context.
# pylint: disable=abstract-method
class _ChangeSceneBase(SimScene):
    """
    Base implementation shared by all transition demo scenes.
    """

    SCENE_ID = "change_scene_base"
    TITLE = "BASE"
    PANEL_COLOR = (0, 0, 0, 220)
    ACCENT_COLOR = (120, 220, 255, 255)

    def __init__(self, ctx: RuntimeContext):
        super().__init__(ctx)
        self._elapsed = 0.0
        self._frames = 0
        self._instance_id = next(_INSTANCE_SEQ)
        self._last_backend_name = "unknown"

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        self._elapsed += dt
        self._frames += 1

        pressed = input_frame.keys_pressed
        if self.context.command_queue is not None:
            for key, target_scene_id in (
                (Key.NUM_1, SCENE_HUB),
                (Key.NUM_2, SCENE_ARENA),
                (Key.NUM_3, SCENE_LAB),
            ):
                if key in pressed and target_scene_id != self.SCENE_ID:
                    self.context.command_queue.push(
                        ChangeSceneCommand(target_scene_id)
                    )

        services = self.context.services
        # pylint: disable=assignment-from-no-return
        vp = services.window.get_viewport()
        stack_lines = list(services.scenes.stack_summary())
        # pylint: enable=assignment-from-no-return

        pulse = (math.sin(self._elapsed * 2.2) + 1.0) * 0.5
        marker_x = int(36 + pulse * 280)

        lines = [
            "scene/change_scene",
            "",
            f"title: {self.TITLE}",
            f"scene_id: {self.SCENE_ID}",
            f"instance_id: {self._instance_id}",
            f"instance_frames: {self._frames}",
            f"instance_elapsed: {self._elapsed:.2f} s",
            f"backend: {self._last_backend_name}",
            f"window: {vp.window_w}x{vp.window_h}",
            "",
            "Press 1/2/3 to enqueue ChangeSceneCommand(...)",
            "SceneAdapter.change() cleans stack and creates a fresh scene instance.",
            "",
            "Visible stack:",
            *([f"  - {line}" for line in stack_lines] or ["  - (empty)"]),
            "",
            "Controls:",
            "  1 -> change_scene_hub",
            "  2 -> change_scene_arena",
            "  3 -> change_scene_lab",
            "  ESC -> quit",
        ]

        def draw(backend: Backend):
            self._last_backend_name = backend.__class__.__name__
            backend.render.draw_rect(18, 18, 760, 470, color=self.PANEL_COLOR)
            backend.render.draw_rect(
                marker_x, 410, 110, 20, color=self.ACCENT_COLOR
            )
            y = 30
            for line in lines:
                backend.text.draw(
                    30,
                    y,
                    line,
                    color=(230, 230, 236),
                    font_size=18,
                )
                y += 21

        return RenderPacket.from_ops([draw])


@register_scene(SCENE_HUB)
class ChangeSceneHub(_ChangeSceneBase):
    """Hub scene that acts as the central navigation entry point."""

    SCENE_ID = SCENE_HUB
    TITLE = "HUB"
    PANEL_COLOR = (8, 14, 34, 225)
    ACCENT_COLOR = (124, 209, 255, 255)


@register_scene(SCENE_ARENA)
class ChangeSceneArena(_ChangeSceneBase):
    """Alternate scene used to demonstrate direct scene transitions."""

    SCENE_ID = SCENE_ARENA
    TITLE = "ARENA"
    PANEL_COLOR = (28, 10, 12, 225)
    ACCENT_COLOR = (255, 170, 138, 255)


@register_scene(SCENE_LAB)
class ChangeSceneLab(_ChangeSceneBase):
    """Secondary scene used to demonstrate branching scene transitions."""

    SCENE_ID = SCENE_LAB
    TITLE = "LAB"
    PANEL_COLOR = (8, 24, 18, 225)
    ACCENT_COLOR = (166, 248, 175, 255)
