"""
Engine runner module.
"""

from __future__ import annotations

from time import sleep
from typing import TYPE_CHECKING

from mini_arcade_core.engine.commands import CommandContext
from mini_arcade_core.engine.loop.config import RunnerConfig
from mini_arcade_core.engine.loop.hooks import LoopHooks
from mini_arcade_core.engine.loop.state import FrameState
from mini_arcade_core.engine.render.context import RenderContext
from mini_arcade_core.engine.render.effects.base import EffectStack
from mini_arcade_core.engine.render.frame_packet import FramePacket
from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.engine.render.pipeline import RenderPipeline
from mini_arcade_core.runtime.capture.video_session import VideoSession
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.utils import FrameTimer, logger

if TYPE_CHECKING:
    from mini_arcade_core.engine.game import Engine


def _neutral_input(frame_index: int, dt: float) -> InputFrame:
    """Create a neutral InputFrame with no input events."""
    return InputFrame(frame_index=frame_index, dt=dt)


def _capture_overlay_packet(
    session: VideoSession,
    *,
    viewport_x: int,
    viewport_y: int,
    viewport_width: int,
) -> RenderPacket:
    """Small built-in capture status overlay shown while capture is busy."""

    def draw(backend):
        compact = session.state == "recording"
        panel_w = min(
            280 if not compact else 228,
            max(176, viewport_width - 24),
        )
        panel_h = 42 if compact else 54
        panel_x = viewport_x + viewport_width - panel_w - 12
        panel_y = viewport_y + 12
        accent = (240, 180, 41)
        if session.state == "encoding":
            accent = (232, 34, 74)

        backend.render.draw_rect(
            panel_x,
            panel_y,
            panel_w,
            panel_h,
            color=(12, 12, 20, 232),
        )
        backend.render.draw_rect(
            panel_x,
            panel_y,
            5,
            panel_h,
            color=accent,
        )
        title = (
            "RECORDING" if session.state == "recording" else "PROCESSING VIDEO"
        )
        backend.text.draw(
            panel_x + 16,
            panel_y + 8,
            title,
            color=(238, 240, 245),
            font_size=12,
        )
        backend.text.draw(
            panel_x + 16,
            panel_y + 22,
            session.message,
            color=(238, 240, 245),
            font_size=10,
        )
        progress = max(0.0, min(1.0, float(getattr(session, "progress", 0.0))))
        if session.state == "encoding":
            bar_x = panel_x + 16
            bar_y = panel_y + panel_h - 11
            bar_w = panel_w - 32
            backend.render.draw_rect(
                bar_x,
                bar_y,
                bar_w,
                4,
                color=(31, 31, 44),
            )
            backend.render.draw_rect(
                bar_x,
                bar_y,
                max(1, int(round(bar_w * progress))),
                4,
                color=accent,
            )

    return RenderPacket(ops=(draw,))


# Justification: This class has many attributes for managing the loop.
# pylint: disable=too-many-instance-attributes
class EngineRunner:
    """
    Core engine runner responsible for the main loop execution.

    :param game: The Engine instance to run.
    :type game: Engine
    :param pipeline: The RenderPipeline to use for rendering.
    :type pipeline: RenderPipeline
    :param effects_stack: The EffectStack for post-processing effects.
    :type effects_stack: EffectStack
    :param hooks: Optional LoopHooks for custom event handling.
    :type hooks: LoopHooks | None
    """

    def __init__(
        self,
        game: "Engine",
        *,
        pipeline: RenderPipeline,
        effects_stack: EffectStack,
        hooks: LoopHooks | None = None,
    ):
        self.game = game
        self.backend = game.backend
        self.services = game.services
        self.managers = game.managers

        self.pipeline = pipeline
        self.effects_stack = effects_stack
        self.hooks = hooks

        self._running = False
        self._packet_cache: dict[int, RenderPacket] = {}

    def stop(self):
        """Stop the engine runner loop."""
        self._running = False

    def run(self, *, cfg: RunnerConfig, timer: FrameTimer | None = None):
        """
        Run the main loop with the given configuration.

        :param cfg: RunnerConfig instance.
        :type cfg: RunnerConfig
        :param timer: Optional FrameTimer for profiling.
        :type timer: FrameTimer | None
        """
        logger.info("EngineRunner starting main loop.")
        self._running = True
        frame = FrameState()

        target_dt = 1.0 / cfg.fps if cfg.fps > 0 else 0.0

        while self._running and self.game.running:
            if (
                cfg.max_frames is not None
                and frame.frame_index >= cfg.max_frames
            ):
                logger.info("EngineRunner reached max_frames limit, stopping.")
                break

            if timer:
                timer.clear()
                timer.mark("frame_start")

            frame.step_time()
            self.services.capture.begin_video_frame(dt=frame.dt)

            events = self._poll_events(timer)
            self._handle_events(events)

            input_frame = self._build_input(events, frame=frame, timer=timer)
            if self._should_quit(input_frame):
                logger.info("Quit signal received, stopping EngineRunner.")
                break

            input_entry = self._input_entry()
            if input_entry is None:
                logger.warning(
                    "No input scene entry found; skipping frame processing."
                )
                break

            self._tick_scenes(
                input_entry, input_frame, frame=frame, timer=timer
            )
            ctx = self._build_command_context(timer)
            self._process_cheats(input_frame, ctx, timer)
            self._execute_commands(ctx, timer)

            self._render_frame(frame, timer)

            self._sleep(target_dt, frame.dt, timer)

            if timer and timer.should_report(frame.frame_index):
                timer.emit(frame.frame_index)

            frame.frame_index += 1

        self.managers.scenes.clean()

    def _poll_events(self, timer: FrameTimer | None):
        # Poll input events from the backend.
        if not hasattr(self.backend, "input") or self.backend.input is None:
            logger.warning("Backend has no input system; no events polled.")
            return []
        events = list(self.backend.input.poll())
        if timer:
            timer.mark("events_polled")
        return events

    def _handle_events(self, events):
        # Handle polled events via hooks if available.
        if self.hooks:
            self.hooks.on_events(events)

    def _build_input(
        self, events, *, frame: FrameState, timer: FrameTimer | None
    ):
        cap = self.services.capture

        if cap.replay_playing:
            input_frame = cap.next_replay_input()

            # optional but recommended: keep runner's frame_index/dt authoritative
            input_frame = InputFrame(
                frame_index=frame.frame_index,
                dt=frame.dt,
                keys_down=input_frame.keys_down,
                keys_pressed=input_frame.keys_pressed,
                keys_released=input_frame.keys_released,
                buttons=input_frame.buttons,
                axes=input_frame.axes,
                mouse_pos=input_frame.mouse_pos,
                mouse_delta=input_frame.mouse_delta,
                text_input=input_frame.text_input,
                quit=input_frame.quit,
            )
        else:
            input_frame = self.services.input.build(
                events, frame.frame_index, frame.dt
            )

        if timer:
            timer.mark("input_built")

        cap.record_input(input_frame)
        return input_frame

    def _should_quit(self, input_frame: InputFrame) -> bool:
        # Determine if the game should quit based on input.
        if not input_frame.quit:
            return False
        return bool(self.services.capture.handle_quit_request())

    def _input_entry(self):
        # Get the current input-focused scene entry.
        return self.managers.scenes.input_entry()

    def _tick_scenes(
        self,
        input_entry,
        input_frame: InputFrame,
        *,
        frame: FrameState,
        timer: FrameTimer | None,
    ):
        # Tick/update all scenes according to their policies.
        if timer:
            timer.mark("tick_start")
        for entry in self.managers.scenes.update_entries():
            effective_input = (
                input_frame
                if entry is input_entry
                else _neutral_input(frame.frame_index, frame.dt)
            )
            packet = entry.scene.tick(effective_input, frame.dt)
            self._packet_cache[id(entry.scene)] = packet
        if timer:
            timer.mark("tick_end")

    def _build_command_context(
        self, timer: FrameTimer | None
    ) -> CommandContext:
        # Build the command execution context.
        if timer:
            timer.mark("command_ctx_start")
        ctx = CommandContext(
            services=self.services,
            managers=self.managers,
            settings=self.game.settings,
            world=self.game.resolve_world(),
        )
        if timer:
            timer.mark("command_ctx_end")
        return ctx

    def _process_cheats(
        self,
        input_frame: InputFrame,
        ctx: CommandContext,
        timer: FrameTimer | None,
    ):
        # Process cheat codes based on the input frame.
        if timer:
            timer.mark("cheats_start")
        self.managers.cheats.process_frame(
            input_frame, context=ctx, queue=self.managers.command_queue
        )
        if timer:
            timer.mark("cheats_end")

    def _execute_commands(self, ctx: CommandContext, timer: FrameTimer | None):
        # Execute all queued commands.
        if timer:
            timer.mark("cmd_exec_start")
        for cmd in self.managers.command_queue.drain():
            cmd.execute(ctx)
        if timer:
            timer.mark("cmd_exec_end")

    def _render_frame(self, frame: FrameState, timer: FrameTimer | None):
        # Render the current frame using the render pipeline.
        if timer:
            timer.mark("render_start")

        vp = self.services.window.get_viewport()

        frame_packets: list[FramePacket] = []
        presentation_packets: list[FramePacket] = []
        for entry in self.managers.scenes.visible_entries():
            scene = entry.scene
            packet = self._packet_cache.get(id(scene))
            if packet is None:
                packet = scene.tick(
                    _neutral_input(frame.frame_index, 0.0), 0.0
                )
                self._packet_cache[id(scene)] = packet

            frame_packets.append(
                FramePacket(
                    scene_id=entry.scene_id,
                    is_overlay=entry.is_overlay,
                    packet=packet,
                )
            )

        capture_session = self.services.capture.current_video_session
        if capture_session is not None and capture_session.state in {
            "recording",
            "finalizing",
            "encoding",
        }:
            presentation_packets.append(
                FramePacket(
                    scene_id="capture_status_overlay",
                    is_overlay=True,
                    packet=_capture_overlay_packet(
                        capture_session,
                        viewport_x=vp.offset_x,
                        viewport_y=vp.offset_y,
                        viewport_width=vp.viewport_w,
                    ),
                )
            )

        render_ctx = RenderContext(
            viewport=vp,
            debug_overlay=getattr(self.game.settings, "debug_overlay", False),
            frame_ms=frame.dt * 1000.0,
        )
        render_ctx.meta["frame_index"] = frame.frame_index
        render_ctx.meta["time_s"] = frame.time_s
        render_ctx.meta["effects_stack"] = self.effects_stack

        self.services.render.last_frame_ms = render_ctx.frame_ms
        self.services.render.last_stats = render_ctx.stats

        self.pipeline.render_frame_content(
            self.backend, render_ctx, frame_packets
        )
        self.services.capture.record_video_frame(
            frame_index=frame.frame_index,
            dt=frame.dt,
        )
        self.pipeline.render_presentation_overlays(
            self.backend,
            render_ctx,
            presentation_packets,
        )
        self.pipeline.present_frame(self.backend, render_ctx)

        if timer:
            timer.mark("render_done")
            timer.mark("end_frame_done")

    def _sleep(self, target_dt: float, dt: float, timer: FrameTimer | None):
        # Sleep to maintain target frame rate if necessary.
        if timer:
            timer.mark("sleep_start")
        if target_dt > 0 and dt < target_dt:
            sleep(target_dt - dt)
        if timer:
            timer.mark("sleep_end")
