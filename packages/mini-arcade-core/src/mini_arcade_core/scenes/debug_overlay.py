"""
Built-in debug overlay scene.
"""

from __future__ import annotations

from mini_arcade_core.backend.backend import Backend
from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.sim_scene import SimScene


def _non_empty(lines: list[str]) -> list[str]:
    out: list[str] = []
    for line in lines:
        text = str(line)
        if not text and (not out or out[-1] == ""):
            continue
        out.append(text)
    while out and out[-1] == "":
        out.pop()
    return out


# Justification: SimScene._get_tick_context is abstract and called by SimScene.tick.
# This scene overrides tick directly.
# pylint: disable=abstract-method
@register_scene("debug_overlay")
class DebugOverlayScene(SimScene):
    """
    Built-in debug overlay whose contents are driven by gameplay settings.
    """

    def __init__(self, ctx: RuntimeContext):
        super().__init__(ctx)
        self._accum = 0.0
        self._frames = 0
        self._fps = 0.0

    def _scene_debug_lines(self, stack: list[object]) -> list[str]:
        lines: list[str] = []
        for entry in stack:
            scene = getattr(entry, "scene", None)
            if scene is self or scene is None:
                continue
            provider = getattr(scene, "debug_overlay_lines", None)
            if not callable(provider):
                continue
            scene_lines = [
                str(line) for line in provider() if str(line).strip()
            ]
            if not scene_lines:
                continue
            lines.append(f"scene[{entry.scene_id}]:")
            lines.extend(f"  {line}" for line in scene_lines)
        return lines

    # pylint: disable=too-many-return-statements
    def _section_lines(
        self, section: str, *, dt: float, services, stack: list[object]
    ) -> list[str]:
        # Justification: service ports are protocol typed, checker does not infer.
        # pylint: disable=assignment-from-no-return
        vp = services.window.get_viewport()
        # pylint: enable=assignment-from-no-return
        rs = services.render

        if section == "timing":
            return [
                f"FPS: {self._fps:5.1f}",
                f"dt: {dt * 1000.0:5.2f} ms",
                f"frame: {rs.last_frame_ms:5.2f} ms",
            ]

        if section == "render":
            return [
                f"renderables: {rs.last_stats.renderables}",
                f"draw_groups~: {rs.last_stats.draw_groups}",
            ]

        if section == "viewport":
            return [
                f"virtual: {vp.virtual_w}x{vp.virtual_h}",
                f"window: {vp.window_w}x{vp.window_h}",
                f"scale: {vp.scale:.3f}",
                f"offset: ({vp.offset_x},{vp.offset_y})",
            ]

        if section == "effects":
            effects_stack = getattr(
                self.context.settings, "effects_stack", None
            )
            if effects_stack is None:
                return []
            active = ",".join(effects_stack.active) or "(none)"
            return [
                f"effects enabled: {effects_stack.enabled}",
                f"effects active: {active}",
            ]

        if section == "stack":
            lines = ["stack:"]
            lines.extend(
                f"  - {entry.scene_id} overlay={entry.is_overlay}"
                for entry in stack
            )
            return lines

        if section == "scene":
            return self._scene_debug_lines(stack)

        return []

    def _build_lines(self, *, dt: float) -> list[str]:
        services = self.context.services
        overlay_cfg = self.context.settings.debug_overlay
        stack = list(services.scenes.visible_entries())
        lines: list[str] = []

        title = str(overlay_cfg.title).strip()
        if title:
            lines.append(title)
            lines.append("")

        if overlay_cfg.static_lines:
            lines.extend(str(line) for line in overlay_cfg.static_lines)
            lines.append("")

        for section in overlay_cfg.sections:
            section_lines = self._section_lines(
                str(section).strip().lower(),
                dt=dt,
                services=services,
                stack=stack,
            )
            if not section_lines:
                continue
            lines.extend(section_lines)
            lines.append("")

        return _non_empty(lines)

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        del input_frame
        self._accum += dt
        self._frames += 1
        if self._accum >= 0.5:
            self._fps = self._frames / self._accum
            self._accum = 0.0
            self._frames = 0

        overlay_cfg = self.context.settings.debug_overlay
        style = overlay_cfg.style
        lines = self._build_lines(dt=dt)

        def draw(backend: Backend):
            panel_height = style.padding * 2 + style.line_height * max(
                len(lines), 1
            )
            backend.render.draw_rect(
                style.x,
                style.y,
                style.width,
                panel_height,
                color=style.panel_color,
            )
            y = style.y + style.padding
            x = style.x + style.padding
            for line in lines:
                backend.text.draw(
                    x,
                    y,
                    line,
                    color=style.text_color,
                    font_size=style.font_size,
                )
                y += style.line_height

        return RenderPacket(ops=[draw])
