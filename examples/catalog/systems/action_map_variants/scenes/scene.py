"""
ActionMap variants scene.

Defines an ActionMap with several binding types and displays the
resulting ActionSnapshot state live.  A small rectangle moves in
response to the mapped actions to demonstrate the full pipeline:
raw keys → ActionMap → ActionSnapshot → entity motion.
"""

from __future__ import annotations

from mini_arcade_core.backend import Backend
from mini_arcade_core.backend.keys import Key
from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.sim_scene import SimScene
from mini_arcade_core.scenes.systems.builtins import (
    ActionMap,
    ActionSnapshot,
    AxisActionBinding,
    DigitalActionBinding,
)

SCENE_ID = "action_map_variants"

_PANEL = (0, 0, 0, 200)
_LABEL = (140, 180, 255)
_VAL = (255, 255, 255)
_ON = (100, 255, 100)
_OFF = (80, 80, 80)

# Build an ActionMap that mixes digital and axis bindings.
ACTION_MAP = ActionMap(
    bindings={
        "confirm": DigitalActionBinding(keys=(Key.ENTER, Key.SPACE)),
        "cancel": DigitalActionBinding(keys=(Key.ESCAPE,)),
        "move_x": AxisActionBinding(
            positive_keys=(Key.D, Key.RIGHT),
            negative_keys=(Key.A, Key.LEFT),
        ),
        "move_y": AxisActionBinding(
            positive_keys=(Key.S, Key.DOWN),
            negative_keys=(Key.W, Key.UP),
        ),
    }
)


@register_scene(SCENE_ID)
class ActionMapVariantsScene(SimScene):
    """Demonstrates ActionMap digital + axis bindings live."""

    def __init__(self, ctx: RuntimeContext):
        super().__init__(ctx)
        self._x = 400.0
        self._y = 300.0
        self._speed = 200.0

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        snapshot: ActionSnapshot = ACTION_MAP.read(input_frame)

        # Move rectangle via mapped axes
        self._x += snapshot.value("move_x") * self._speed * dt
        self._y += snapshot.value("move_y") * self._speed * dt
        self._x = max(0.0, min(780.0, self._x))
        self._y = max(0.0, min(580.0, self._y))

        def draw(backend: Backend):
            r = backend.render
            t = backend.text

            r.draw_rect(16, 16, 768, 568, color=_PANEL)

            y = 28
            t.draw(24, y, "ActionMap Variants", color=_LABEL)
            y += 32

            # Digital actions
            for action_id in ("confirm", "cancel"):
                state = snapshot.state(action_id)
                col = _ON if state.down else _OFF
                t.draw(24, y, f"{action_id}:", color=_LABEL)
                parts = []
                if state.down:
                    parts.append("DOWN")
                if state.pressed:
                    parts.append("PRESSED")
                if state.released:
                    parts.append("RELEASED")
                t.draw(200, y, " | ".join(parts) or "idle", color=col)
                y += 22

            y += 8
            # Axis actions
            for action_id in ("move_x", "move_y"):
                val = snapshot.value(action_id)
                bar_w = int(abs(val) * 100)
                t.draw(24, y, f"{action_id}: {val:+.2f}", color=_LABEL)
                bar_x = 250
                bar_col = (80, 200, 80) if val >= 0 else (200, 80, 80)
                if val >= 0:
                    r.draw_rect(bar_x, y + 2, bar_w, 14, color=bar_col)
                else:
                    r.draw_rect(bar_x - bar_w, y + 2, bar_w, 14, color=bar_col)
                y += 22

            y += 16
            t.draw(24, y, "Move with WASD / Arrow keys", color=_VAL)
            y += 20
            t.draw(24, y, "Confirm: Enter/Space  Cancel: Escape", color=_VAL)

            # Moving indicator
            r.draw_rect(
                int(self._x),
                int(self._y),
                20,
                20,
                color=(255, 200, 60),
            )

        return RenderPacket.from_ops([draw])
