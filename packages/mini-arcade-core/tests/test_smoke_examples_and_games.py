from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import pytest


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _bootstrap_repo_imports() -> None:
    root = _repo_root()
    candidates = [root]
    candidates.extend(path for path in (root / "packages").glob("*/src"))
    candidates.extend(path for path in (root / "games").glob("*/src"))
    candidates.extend(path for path in (root / "originals").glob("*/src"))

    for path in reversed(candidates):
        value = str(path)
        if value not in sys.path:
            sys.path.insert(0, value)


_bootstrap_repo_imports()

from examples._shared import runner as example_runner  # noqa: E402
from examples._shared.runner import load_example_spec  # noqa: E402
from examples._shared.spec import ExampleSpec  # noqa: E402
from mini_arcade.modules.game_paths import (  # noqa: E402
    find_game_dir,
    game_settings_candidates,
)
from mini_arcade.modules.game_runner.processors import (  # noqa: E402
    _discover_example_ids,
)
from mini_arcade.modules.settings import Settings  # noqa: E402
from mini_arcade_core.backend.events import Event, EventType  # noqa: E402
from mini_arcade_core.backend.keys import Key  # noqa: E402
from mini_arcade_core.engine.engine_config import (  # noqa: E402
    EngineConfig,
    SceneConfig,
)
from mini_arcade_core.engine.game import (  # noqa: E402
    Engine,
    EngineDependencies,
)
from mini_arcade_core.engine.render.packet import RenderPacket  # noqa: E402
from mini_arcade_core.runtime.context import RuntimeContext  # noqa: E402
from mini_arcade_core.runtime.input_frame import InputFrame  # noqa: E402
from mini_arcade_core.scenes.autoreg import register_scene  # noqa: E402
from mini_arcade_core.scenes.registry import SceneRegistry  # noqa: E402
from mini_arcade_core.scenes.sim_scene import SimScene  # noqa: E402

EXAMPLE_IDS = tuple(
    _discover_example_ids(_repo_root() / "examples" / "catalog")
)
LEGACY_KEY_PATTERN = re.compile(r"\bKey\.(?:RETURN|K_[0-9]+)\b")

GAME_CASES = [
    ("deja-bounce", ("menu", "pong")),
    ("space-invaders", ("space_invaders_menu", "space_invaders")),
    ("asteroids", ("asteroids_menu", "asteroids")),
    ("pong", ("menu", "play")),
    ("breakout", ("menu", "play")),
    ("pacman", ("menu", "play")),
    ("snake", ("menu", "play")),
    ("tetris", ("menu", "play")),
    ("office-horrors", ("office_horrors_menu", "office_horrors")),
]


def _game_settings_path(game_id: str) -> Path:
    candidates = tuple(game_settings_candidates(_repo_root(), game_id))
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "No settings file found for game "
        f"{game_id!r}. Searched: "
        + ", ".join(str(path) for path in candidates)
    )


def _missing_game_cases() -> list[str]:
    missing: list[str] = []
    for game_id, _scene_ids in GAME_CASES:
        game_dir = find_game_dir(_repo_root(), game_id)
        try:
            _game_settings_path(game_id)
        except FileNotFoundError:
            missing.append(f"{game_id}:missing-settings")
            continue
        if game_dir is None or not (game_dir / "src").is_dir():
            missing.append(f"{game_id}:missing-src")
    return missing


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
class _QueuedFakeInput:
    events_by_frame: list[list[Event]]
    frame_index: int = 0

    def poll(self) -> Iterable[Event]:
        if self.frame_index < len(self.events_by_frame):
            events = self.events_by_frame[self.frame_index]
        else:
            events = []
        self.frame_index += 1
        return list(events)


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
        self,
        text: str,
        font_size: int | None = None,
        font_name: str | None = None,
    ) -> tuple[int, int]:
        _ = font_name
        size = int(font_size or 16)
        return (max(len(text), 1) * max(size // 2, 1), size)

    def draw(
        self,
        x: int,
        y: int,
        text: str,
        color=(255, 255, 255),
        font_size: int | None = None,
        font_name: str | None = None,
    ):
        _ = (x, y, text, color, font_size, font_name)
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


_ESCAPE_VISITED: list[str] = []


@register_scene("test_escape_source")
class _EscapeSourceScene(SimScene):
    def on_enter(self):
        _ESCAPE_VISITED.append("source")

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        del input_frame, dt
        return RenderPacket.from_ops([])


@register_scene("test_escape_target")
class _EscapeTargetScene(SimScene):
    def on_enter(self):
        _ESCAPE_VISITED.append("target")

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        del input_frame, dt
        return RenderPacket.from_ops([])


@register_scene("test_escape_menu")
class _EscapeMenuScene(SimScene):
    def uses_builtin_escape_handling(self) -> bool:
        return False

    def on_enter(self):
        _ESCAPE_VISITED.append("menu")

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        del input_frame, dt
        return RenderPacket.from_ops([])


def test_catalog_examples_smoke() -> None:
    assert "systems/action_map_variants" in EXAMPLE_IDS
    assert "systems/cull_viewport_builtin" in EXAMPLE_IDS
    assert "systems/pause_intent_builtin" in EXAMPLE_IDS

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


def test_example_runner_propagates_run_game_failures(
    monkeypatch,
) -> None:
    class _StubSettings:
        def gameplay_defaults(self) -> dict[str, object]:
            return {}

    spec = ExampleSpec(
        discover_packages=["tests.fake_scenes"],
        initial_scene="main",
        fps=60,
        backend_factory=lambda: object(),
    )

    def _fake_load_example_spec(example_id: str, **kwargs) -> ExampleSpec:
        del kwargs
        assert example_id == "tests/failing_example"
        return spec

    def _fake_for_example(
        example_id: str,
        required: bool = False,
    ) -> _StubSettings:
        assert example_id == "tests/failing_example"
        assert required is False
        return _StubSettings()

    def _broken_run_game(**kwargs) -> None:
        del kwargs
        raise RuntimeError("runner boom")

    monkeypatch.setattr(
        example_runner, "load_example_spec", _fake_load_example_spec
    )
    monkeypatch.setattr(
        example_runner.Settings, "for_example", _fake_for_example
    )
    monkeypatch.setattr(example_runner, "run_game", _broken_run_game)

    with pytest.raises(RuntimeError, match="runner boom"):
        example_runner.run_example("tests/failing_example")


def test_examples_use_canonical_key_names() -> None:
    offenders: list[str] = []
    examples_dir = _repo_root() / "examples" / "catalog"

    for path in sorted(examples_dir.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        if LEGACY_KEY_PATTERN.search(text):
            offenders.append(str(path.relative_to(_repo_root())))

    assert offenders == []


def test_games_smoke() -> None:
    missing = _missing_game_cases()
    if missing:
        pytest.skip(
            "games/ content not available in this checkout: "
            + ", ".join(missing)
        )

    for game_id, scene_ids in GAME_CASES:
        settings = Settings(
            config_path=_game_settings_path(game_id),
            required=True,
            force_reload=True,
        )
        scene_config = SceneConfig.from_dict(settings.scene_defaults())
        engine_config = EngineConfig.from_dict(
            settings.engine_config_defaults()
        )
        gameplay_config = settings.gameplay_defaults()

        for scene_id in scene_ids:
            _run_scene(
                scene_id=scene_id,
                discover_packages=list(scene_config.discover_packages),
                engine_config=engine_config,
                gameplay_config=gameplay_config,
            )


def test_scene_escape_config_changes_scene() -> None:
    _ESCAPE_VISITED.clear()
    backend = _FakeBackend(
        input=_QueuedFakeInput(
            events_by_frame=[
                [Event(type=EventType.KEYDOWN, key=Key.ESCAPE)],
                [Event(type=EventType.QUIT)],
            ]
        )
    )
    registry = SceneRegistry(_factories={})
    registry.register_cls("test_escape_source", _EscapeSourceScene)
    registry.register_cls("test_escape_target", _EscapeTargetScene)
    engine = Engine(
        EngineConfig(fps=60),
        EngineDependencies(
            backend=backend,
            scene_registry=registry.discover("mini_arcade_core.scenes"),
            gameplay_settings={
                "scenes": {
                    "test_escape_source": {
                        "escape": {
                            "command": "change_scene",
                            "scene_id": "test_escape_target",
                        }
                    }
                }
            },
        ),
    )
    engine.run(initial_scene="test_escape_source")
    assert _ESCAPE_VISITED[:2] == ["source", "target"]


def test_scene_escape_config_skips_scene_opt_out() -> None:
    _ESCAPE_VISITED.clear()
    backend = _FakeBackend(
        input=_QueuedFakeInput(
            events_by_frame=[
                [Event(type=EventType.KEYDOWN, key=Key.ESCAPE)],
                [Event(type=EventType.QUIT)],
            ]
        )
    )
    registry = SceneRegistry(_factories={})
    registry.register_cls("test_escape_menu", _EscapeMenuScene)
    registry.register_cls("test_escape_target", _EscapeTargetScene)
    engine = Engine(
        EngineConfig(fps=60),
        EngineDependencies(
            backend=backend,
            scene_registry=registry,
            gameplay_settings={
                "scenes": {
                    "test_escape_menu": {
                        "escape": {
                            "command": "change_scene",
                            "scene_id": "test_escape_target",
                        }
                    }
                }
            },
        ),
    )
    engine.run(initial_scene="test_escape_menu")
    assert _ESCAPE_VISITED == ["menu"]
