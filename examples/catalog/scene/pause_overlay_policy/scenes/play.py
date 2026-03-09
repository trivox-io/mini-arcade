"""
Gameplay scene for scene/pause_overlay_policy tutorial example.
"""

from __future__ import annotations

import math

from mini_arcade_core.backend.backend import Backend
from mini_arcade_core.backend.keys import Key
from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.sim_scene import SimScene

from .commands import PauseOverlayCommand

SCENE_ID = "pause_overlay_policy_play"


# Justification: This scene overrides tick directly and does not use a tick context.
# pylint: disable=abstract-method
@register_scene(SCENE_ID)
class PauseOverlayPolicyPlayScene(SimScene):
    """
    Base scene used to demonstrate pause overlay blocking policy.
    """

    def __init__(self, ctx: RuntimeContext):
        super().__init__(ctx)
        self._elapsed = 0.0
        self._frames = 0
        self._last_backend_name = "unknown"

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        self._elapsed += dt
        self._frames += 1

        if (
            self.context.command_queue is not None
            and (
                Key.P in input_frame.keys_pressed
                or Key.ESCAPE in input_frame.keys_pressed
            )
        ):
            self.context.command_queue.push(PauseOverlayCommand())

        services = self.context.services
        # pylint: disable=assignment-from-no-return
        vp = services.window.get_viewport()
        input_owner = services.scenes.input_entry()
        stack_lines = list(services.scenes.stack_summary())
        # pylint: enable=assignment-from-no-return

        pulse = (math.sin(self._elapsed * 2.0) + 1.0) * 0.5
        bar_x = int(56 + pulse * 330)
        owner_id = input_owner.scene_id if input_owner else "(none)"

        lines = [
            "scene/pause_overlay_policy",
            "",
            f"scene: {SCENE_ID}",
            f"backend: {self._last_backend_name}",
            f"frame: {self._frames}",
            f"elapsed: {self._elapsed:.2f} s",
            f"input owner: {owner_id}",
            f"window: {vp.window_w}x{vp.window_h}",
            "",
            "Press P or ESC to push pause overlay.",
            "While pause overlay is active:",
            "  - this scene stops ticking (blocks_update=True)",
            "  - this scene stops receiving input (blocks_input=True)",
            "",
            "Visible stack:",
            *([f"  - {line}" for line in stack_lines] or ["  - (empty)"]),
            "",
            "Controls:",
            "  P or ESC -> pause overlay",
            "  F1 -> debug overlay",
        ]

        def draw(backend: Backend):
            self._last_backend_name = backend.__class__.__name__
            backend.render.draw_rect(18, 18, 760, 470, color=(0, 0, 0, 220))
            backend.render.draw_rect(bar_x, 410, 120, 22, color=(118, 210, 255, 255))
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

