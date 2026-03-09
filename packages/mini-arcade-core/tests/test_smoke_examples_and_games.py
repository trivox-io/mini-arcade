from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _bootstrap_repo_imports() -> None:
    root = _repo_root()
    candidates = [root]
    candidates.extend(path for path in (root / "packages").glob("*/src"))
    candidates.extend(path for path in (root / "games").glob("*/src"))

    for path in reversed(candidates):
        value = str(path)
        if value not in sys.path:
            sys.path.insert(0, value)


_bootstrap_repo_imports()

from examples._shared.runner import load_example_spec  # noqa: E402
from mini_arcade.modules.settings import Settings  # noqa: E402
from mini_arcade_core.backend.events import Event, EventType  # noqa: E402
from mini_arcade_core.engine.engine_config import (  # noqa: E402
    EngineConfig,
    SceneConfig,
)
from mini_arcade_core.engine.game import (  # noqa: E402
    Engine,
    EngineDependencies,
)
from mini_arcade_core.scenes.registry import SceneRegistry  # noqa: E402


EXAMPLE_IDS = [
    "config/backend_swap",
    "config/engine_config_basics",
    "scene/change_scene",
    "scene/debug_overlay_builtin",
    "scene/menu_scene_base",
    "scene/minimal_scene",
    "scene/pause_overlay_policy",
    "window/fit_vs_fill",
    "window/resize_reflow",
    "window/screen_to_virtual_input",
    "window/virtual_resolution_basics",
]

GAME_CASES = [
    ("deja-bounce", ("menu", "pong")),
    ("space-invaders", ("space_invaders_menu", "space_invaders")),
    ("asteroids", ("asteroids_menu", "asteroids")),
    ("office-horrors", ("office_horrors_menu", "office_horrors")),
]


@dataclass
class _FakeWindow:
    width: int = 960
    height: int = 540
    title: str = "Smoke Test"

    def set_title(self, title: str) -> None:
        self.title = title

    def resize(self, width: int, height: int) -> None:
        self.width = int(width)
        self.height = int(height)

    def size(self) -> tuple[int, int]:
        return (self.width, self.height)

    def drawable_size(self) -> tuple[int, int]:
        return (self.width, self.height)


@dataclass
class _FakeInput:
    frame_index: int = 0

    def poll(self) -> Iterable[Event]:
        self.frame_index += 1
        if self.frame_index >= 3:
            return [Event(type=EventType.QUIT)]
        return []


@dataclass
class _FakeRender:
    next_texture_id: int = 1
    background_color: tuple[int, int, int] = (0, 0, 0)
    frame_count: int = 0
    clip_rect: tuple[int, int, int, int] | None = None
    textures: dict[int, tuple[int, int]] = field(default_factory=dict)

    def set_clear_color(self, r: int, g: int, b: int) -> None:
        self.background_color = (int(r), int(g), int(b))

    def begin_frame(self) -> None:
        self.frame_count += 1

    def end_frame(self) -> None:
        return None

    def draw_rect(self, x: int, y: int, w: int, h: int, color=(255, 255, 255)):
        return None

    def draw_line(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color=(255, 255, 255),
        thickness: int = 1,
    ):
        return None

    def set_clip_rect(self, x: int, y: int, w: int, h: int):
        self.clip_rect = (int(x), int(y), int(w), int(h))

    def clear_clip_rect(self):
        self.clip_rect = None

    def create_texture_rgba(
        self, w: int, h: int, pixels: bytes, pitch: int | None = None
    ) -> int:
        texture_id = self.next_texture_id
        self.next_texture_id += 1
        self.textures[texture_id] = (int(w), int(h))
        return texture_id

    def destroy_texture(self, tex: int) -> None:
        self.textures.pop(int(tex), None)

    def draw_texture(
        self,
        tex: int,
        x: int,
        y: int,
        w: int,
        h: int,
        angle_deg: float = 0.0,
    ):
        return None

    def draw_texture_tiled_y(
        self, tex_id: int, x: int, y: int, w: int, h: int
    ):
        return None

    def draw_circle(self, x: int, y: int, radius: int, color=(255, 255, 255)):
        return None

    def draw_poly(
        self,
        points: list[tuple[int, int]],
        color=(255, 255, 255),
        filled: bool = True,
    ):
        return None


@dataclass
class _FakeText:
    def measure(
        self, text: str, font_size: int | None = None
    ) -> tuple[int, int]:
        size = int(font_size or 16)
        return (max(len(text), 1) * max(size // 2, 1), size)

    def draw(
        self,
        x: int,
        y: int,
        text: str,
        color=(255, 255, 255),
        font_size: int | None = None,
    ):
        return None


@dataclass
class _FakeAudio:
    sounds: dict[str, str] = field(default_factory=dict)

    def init(
        self, frequency: int = 44100, channels: int = 2, chunk_size: int = 2048
    ):
        return None

    def shutdown(self):
        return None

    def load_sound(self, sound_id: str, path: str):
        self.sounds[str(sound_id)] = str(path)

    def play_sound(self, sound_id: str, loops: int = 0):
        return None

    def set_master_volume(self, volume: int):
        return None

    def set_sound_volume(self, sound_id: str, volume: int):
        return None

    def stop_all(self):
        return None


@dataclass
class _FakeCapture:
    def bmp(self, path: str | None = None) -> bool:
        return True

    def argb8888_bytes(self) -> tuple[int, int, bytes]:
        return (1, 1, b"\x00\x00\x00\x00")


@dataclass
class _FakeBackend:
    window: _FakeWindow = field(default_factory=_FakeWindow)
    input: _FakeInput = field(default_factory=_FakeInput)
    render: _FakeRender = field(default_factory=_FakeRender)
    text: _FakeText = field(default_factory=_FakeText)
    audio: _FakeAudio = field(default_factory=_FakeAudio)
    capture: _FakeCapture = field(default_factory=_FakeCapture)
    initialized: bool = False
    viewport_transform: tuple[int, int, float] = (0, 0, 1.0)

    def init(self):
        self.initialized = True

    def set_viewport_transform(
        self, offset_x: int, offset_y: int, scale: float
    ):
        self.viewport_transform = (
            int(offset_x),
            int(offset_y),
            float(scale),
        )

    def clear_viewport_transform(self):
        self.viewport_transform = (0, 0, 1.0)

    def set_clip_rect(self, x: int, y: int, w: int, h: int):
        self.render.set_clip_rect(x, y, w, h)

    def clear_clip_rect(self):
        self.render.clear_clip_rect()


def _run_scene(
    *,
    scene_id: str,
    discover_packages: list[str],
    engine_config: EngineConfig,
    gameplay_config: dict[str, object] | None = None,
) -> _FakeBackend:
    backend = _FakeBackend()
    engine = Engine(
        engine_config,
        EngineDependencies(
            backend=backend,
            scene_registry=SceneRegistry(_factories={}).discover(
                *discover_packages
            ),
            gameplay_settings=gameplay_config,
        ),
    )
    engine.run(initial_scene=scene_id)
    assert backend.render.frame_count >= 1
    return backend


def test_catalog_examples_smoke() -> None:
    for example_id in EXAMPLE_IDS:
        spec = load_example_spec(example_id)
        settings = Settings.for_example(
            example_id, required=False, force_reload=True
        )
        engine_config = (
            spec.engine_config_factory(None)
            if spec.engine_config_factory is not None
            else EngineConfig(fps=spec.fps)
        )
        _run_scene(
            scene_id=spec.initial_scene,
            discover_packages=list(spec.discover_packages),
            engine_config=engine_config,
            gameplay_config=settings.gameplay_defaults(),
        )


def test_games_smoke() -> None:
    for game_id, scene_ids in GAME_CASES:
        settings = Settings.for_game(game_id, required=True, force_reload=True)
        scene_config = SceneConfig.from_dict(settings.scene_defaults())
        engine_config = EngineConfig.from_dict(settings.engine_config_defaults())
        gameplay_config = settings.gameplay_defaults()

        for scene_id in scene_ids:
            _run_scene(
                scene_id=scene_id,
                discover_packages=list(scene_config.discover_packages),
                engine_config=engine_config,
                gameplay_config=gameplay_config,
            )
