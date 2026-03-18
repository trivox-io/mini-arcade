from __future__ import annotations

from dataclasses import dataclass, field

from mini_arcade_core.engine.commands import CommandQueue
from mini_arcade_core.engine.gameplay_settings import GamePlaySettings
from mini_arcade_core.engine.render.camera import (
    Camera2D,
    camera_from_packet,
    packet_with_camera,
    screen_to_world,
    viewport_transform_for_camera,
    world_to_screen,
)
from mini_arcade_core.engine.render.context import RenderContext
from mini_arcade_core.engine.render.frame_packet import FramePacket
from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.engine.render.passes.world import WorldPass
from mini_arcade_core.engine.render.viewport import ViewportMode, ViewportState
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.sim_scene import (
    BaseTickContext,
    BaseWorld,
    SimScene,
)
from mini_arcade_core.scenes.systems.builtins.capture_hotkeys import (
    CaptureHotkey,
    SceneCaptureConfig,
)
from mini_arcade_core.scenes.systems.phases import SystemPhase
from mini_arcade_core.spaces.math.vec2 import Vec2


def _viewport_state() -> ViewportState:
    return ViewportState(
        virtual_w=320,
        virtual_h=180,
        window_w=640,
        window_h=360,
        mode=ViewportMode.FIT,
        scale=2.0,
        viewport_w=640,
        viewport_h=360,
        offset_x=0,
        offset_y=0,
    )


def test_camera_transform_and_coordinate_helpers_round_trip() -> None:
    viewport = _viewport_state()
    camera = Camera2D(center=Vec2(100.0, 50.0), zoom=1.5)

    transform = viewport_transform_for_camera(viewport, camera)

    assert transform.s == 3.0
    assert transform.ox == 20
    assert transform.oy == 30

    screen = world_to_screen(viewport, 100.0, 50.0, camera=camera)
    assert screen == (320.0, 180.0)

    world = screen_to_world(viewport, 320.0, 180.0, camera=camera)
    assert world == (100.0, 50.0)


def test_world_pass_uses_camera_transform_after_viewport_clip_setup() -> None:
    viewport = _viewport_state()
    camera = Camera2D(center=Vec2(120.0, 60.0), zoom=2.0)
    packet = packet_with_camera(
        RenderPacket.from_ops([lambda backend: backend.log.append(("draw",))]),
        camera,
    )

    @dataclass
    class _FakeRender:
        log: list[tuple[object, ...]]

        def set_clip_rect(self, x: int, y: int, w: int, h: int) -> None:
            self.log.append(("clip", x, y, w, h))

        def clear_clip_rect(self) -> None:
            self.log.append(("clear_clip",))

    @dataclass
    class _FakeBackend:
        log: list[tuple[object, ...]] = field(default_factory=list)

        def __post_init__(self) -> None:
            self.render = _FakeRender(self.log)

        def set_viewport_transform(
            self, offset_x: int, offset_y: int, scale: float
        ) -> None:
            self.log.append(("vp", offset_x, offset_y, scale))

        def clear_viewport_transform(self) -> None:
            self.log.append(("clear_vp",))

    backend = _FakeBackend()
    WorldPass().run(
        backend,
        RenderContext(viewport=viewport),
        [FramePacket(scene_id="main", is_overlay=False, packet=packet)],
    )

    assert backend.log[:4] == [
        ("vp", 0, 0, 2.0),
        ("clip", 0, 0, 320, 180),
        ("vp", -160, -60, 4.0),
        ("draw",),
    ]
    assert backend.log[-2:] == [("clear_clip",), ("clear_vp",)]


def test_sim_scene_attaches_world_camera_to_render_packet() -> None:
    @dataclass
    class _World(BaseWorld):
        camera: Camera2D = field(
            default_factory=lambda: Camera2D(
                center=Vec2(48.0, 24.0),
                zoom=1.25,
            )
        )

    @dataclass
    class _Ctx(BaseTickContext[_World, object]):
        pass

    @dataclass
    class _PacketSystem:
        name: str = "packet"
        phase: int = SystemPhase.RENDERING
        order: int = 100

        def step(self, ctx: _Ctx):
            ctx.packet = RenderPacket.from_ops([])

    class _Scene(SimScene[_Ctx, _World]):
        tick_context_type = _Ctx
        capture_config = SceneCaptureConfig(
            screenshot=CaptureHotkey(enabled=False),
            video_toggle=CaptureHotkey(enabled=False),
            replay_record_toggle=CaptureHotkey(enabled=False),
            replay_play_toggle=CaptureHotkey(enabled=False),
        )

        def on_enter(self):
            self.world = _World(entities=[])
            self.systems.add(_PacketSystem())

    scene = _Scene(
        RuntimeContext(
            services=None,  # type: ignore[arg-type]
            config=None,  # type: ignore[arg-type]
            settings=GamePlaySettings(),
            command_queue=CommandQueue(),
            cheats=None,
        )
    )
    scene.on_enter()

    packet = scene.tick(InputFrame(frame_index=0, dt=1 / 60), 1 / 60)

    assert camera_from_packet(packet) == scene.world.camera
