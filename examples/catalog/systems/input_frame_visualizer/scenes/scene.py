"""
InputFrame visualizer scene.

Renders a live dashboard of InputFrame state each tick:
keys held, keys pressed/released, mouse position, axes, and buttons.
"""

from __future__ import annotations

from mini_arcade_core.backend import Backend
from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.sim_scene import SimScene

SCENE_ID = "input_frame_visualizer"

_PANEL_COLOR = (0, 0, 0, 200)
_LABEL_COLOR = (140, 180, 255)
_VALUE_COLOR = (255, 255, 255)
_PRESSED_COLOR = (100, 255, 100)
_RELEASED_COLOR = (255, 100, 100)


@register_scene(SCENE_ID)
class InputFrameVisualizerScene(SimScene):
    """Displays a live view of the current InputFrame."""

    def __init__(self, ctx: RuntimeContext):
        super().__init__(ctx)
        self._frame_count = 0

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        self._frame_count += 1
        frame = input_frame

        def draw(backend: Backend):
            r = backend.render
            t = backend.text

            # Background panel
            r.draw_rect(16, 16, 768, 568, color=_PANEL_COLOR)

            y = 28
            t.draw(24, y, "InputFrame Visualizer", color=_LABEL_COLOR)
            y += 28

            t.draw(
                24, y, f"frame_index: {frame.frame_index}", color=_VALUE_COLOR
            )
            t.draw(400, y, f"dt: {frame.dt:.4f}", color=_VALUE_COLOR)
            y += 24

            # Keys down
            keys_down_names = sorted(k.name for k in frame.keys_down)
            t.draw(24, y, "keys_down:", color=_LABEL_COLOR)
            y += 20
            t.draw(
                40,
                y,
                ", ".join(keys_down_names) or "(none)",
                color=_VALUE_COLOR,
            )
            y += 24

            # Keys pressed this frame
            keys_pressed_names = sorted(k.name for k in frame.keys_pressed)
            t.draw(24, y, "keys_pressed:", color=_LABEL_COLOR)
            y += 20
            t.draw(
                40,
                y,
                ", ".join(keys_pressed_names) or "(none)",
                color=_PRESSED_COLOR,
            )
            y += 24

            # Keys released this frame
            keys_released_names = sorted(k.name for k in frame.keys_released)
            t.draw(24, y, "keys_released:", color=_LABEL_COLOR)
            y += 20
            t.draw(
                40,
                y,
                ", ".join(keys_released_names) or "(none)",
                color=_RELEASED_COLOR,
            )
            y += 28

            # Mouse
            mx, my = frame.mouse_pos
            mdx, mdy = frame.mouse_delta
            t.draw(24, y, f"mouse_pos: ({mx}, {my})", color=_VALUE_COLOR)
            t.draw(400, y, f"mouse_delta: ({mdx}, {mdy})", color=_VALUE_COLOR)
            y += 28

            # Axes
            t.draw(24, y, "axes:", color=_LABEL_COLOR)
            y += 20
            if frame.axes:
                for axis_name, axis_val in sorted(frame.axes.items()):
                    t.draw(
                        40,
                        y,
                        f"{axis_name}: {axis_val:+.3f}",
                        color=_VALUE_COLOR,
                    )
                    y += 20
            else:
                t.draw(40, y, "(none)", color=_VALUE_COLOR)
                y += 20
            y += 8

            # Buttons
            t.draw(24, y, "buttons:", color=_LABEL_COLOR)
            y += 20
            if frame.buttons:
                for btn_name, btn_state in sorted(frame.buttons.items()):
                    state_parts = []
                    if btn_state.down:
                        state_parts.append("DOWN")
                    if btn_state.pressed:
                        state_parts.append("PRESSED")
                    if btn_state.released:
                        state_parts.append("RELEASED")
                    label = " | ".join(state_parts) or "idle"
                    t.draw(40, y, f"{btn_name}: {label}", color=_VALUE_COLOR)
                    y += 20
            else:
                t.draw(40, y, "(none)", color=_VALUE_COLOR)
                y += 20
            y += 8

            # Text input
            t.draw(
                24, y, f"text_input: '{frame.text_input}'", color=_VALUE_COLOR
            )
            y += 24
            t.draw(24, y, f"quit: {frame.quit}", color=_VALUE_COLOR)

        return RenderPacket.from_ops([draw])
