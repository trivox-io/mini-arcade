from __future__ import annotations

from types import SimpleNamespace

from mini_arcade_core.engine.loop.runner import EngineRunner
from mini_arcade_core.engine.loop.state import FrameState
from mini_arcade_core.engine.render.packet import RenderPacket


class _SceneStub:
    def tick(self, *_args, **_kwargs):
        raise AssertionError(
            "cached packets should be reused during this test"
        )


class _SceneQueryStub:
    def __init__(self, entries):
        self._entries = list(entries)

    def visible_entries(self):
        return list(self._entries)


class _PipelineStub:
    def __init__(self, log):
        self.log = log

    def render_frame_content(self, _backend, _ctx, packets) -> None:
        self.log.append(("content", [packet.scene_id for packet in packets]))

    def render_presentation_overlays(self, _backend, _ctx, packets) -> None:
        self.log.append(("overlay", [packet.scene_id for packet in packets]))

    def present_frame(self, _backend, _ctx) -> None:
        self.log.append(("present",))


class _CaptureServiceStub:
    def __init__(self, log, session):
        self.log = log
        self.current_video_session = session

    def record_video_frame(self, *, frame_index: int, dt: float) -> None:
        self.log.append(("capture", frame_index, dt))


def _build_runner(*, log, session):
    arena_scene = _SceneStub()
    hud_scene = _SceneStub()
    entries = [
        SimpleNamespace(scene=arena_scene, scene_id="arena", is_overlay=False),
        SimpleNamespace(scene=hud_scene, scene_id="hud", is_overlay=True),
    ]
    viewport = SimpleNamespace(
        offset_x=0,
        offset_y=0,
        viewport_w=540,
        viewport_h=960,
    )
    services = SimpleNamespace(
        window=SimpleNamespace(get_viewport=lambda: viewport),
        capture=_CaptureServiceStub(log, session),
        render=SimpleNamespace(last_frame_ms=0.0, last_stats=None),
    )
    game = SimpleNamespace(
        backend=SimpleNamespace(),
        services=services,
        managers=SimpleNamespace(scenes=_SceneQueryStub(entries)),
        settings=SimpleNamespace(debug_overlay=False),
    )
    runner = EngineRunner(
        game,
        pipeline=_PipelineStub(log),
        effects_stack=object(),
    )
    runner._packet_cache[id(arena_scene)] = RenderPacket.from_ops(
        [lambda backend: None]
    )
    runner._packet_cache[id(hud_scene)] = RenderPacket.from_ops(
        [lambda backend: None]
    )
    return runner


def test_runner_draws_capture_overlay_only_after_frame_capture() -> None:
    log: list[tuple[object, ...]] = []
    session = SimpleNamespace(
        state="recording",
        message="Recording in progress.",
        progress=0.0,
    )
    runner = _build_runner(log=log, session=session)

    runner._render_frame(
        FrameState(frame_index=7, time_s=1.25, dt=1 / 60), timer=None
    )

    assert log == [
        ("content", ["arena", "hud"]),
        ("capture", 7, 1 / 60),
        ("overlay", ["capture_status_overlay"]),
        ("present",),
    ]


def test_runner_skips_presentation_overlay_when_capture_is_idle() -> None:
    log: list[tuple[object, ...]] = []
    runner = _build_runner(log=log, session=None)

    runner._render_frame(
        FrameState(frame_index=3, time_s=0.5, dt=1 / 30), timer=None
    )

    assert log == [
        ("content", ["arena", "hud"]),
        ("capture", 3, 1 / 30),
        ("overlay", []),
        ("present",),
    ]
