"""
Example: config/engine_config_basics
"""

from __future__ import annotations

from typing import Any

from examples._shared.defaults import make_backend_factory
from examples._shared.spec import ExampleSpec
from mini_arcade.modules.settings import Settings
from mini_arcade_core import EngineConfig
from mini_arcade_core.engine.engine_config import PostFXConfig

EXAMPLE_ID = "config/engine_config_basics"
DEFAULT_SCENE_ID = "engine_config_basics"
DEFAULT_DISCOVER_PACKAGES = [
    "examples.catalog.config.engine_config_basics",
    "mini_arcade_core.scenes",
]


def _list_arg(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str):
        return [token.strip() for token in value.split(",") if token.strip()]
    return [str(value)]


def _arg_or_default(
    kwargs: dict[str, Any], key: str, default: Any
) -> Any:
    value = kwargs.get(key, default)
    return default if value is None else value


def _rgb_or_default(
    value: object, default: tuple[int, int, int]
) -> tuple[int, int, int]:
    if (
        isinstance(value, (list, tuple))
        and len(value) >= 3
    ):
        return (int(value[0]), int(value[1]), int(value[2]))
    return default


def build_example(**kwargs) -> ExampleSpec:
    """
    Build the tutorial spec for engine configuration basics.
    """
    settings = Settings.for_example(EXAMPLE_ID, required=False)
    engine_defaults = settings.engine_config_defaults()
    scene_defaults = settings.scene_defaults()
    backend_defaults = settings.backend_defaults(resolve_paths=True)

    backend = str(
        _arg_or_default(
            kwargs,
            "backend",
            backend_defaults.get("provider", "pygame"),
        )
    ).lower().strip()

    fps = int(_arg_or_default(kwargs, "fps", engine_defaults.get("fps", 60)))
    virtual_resolution = engine_defaults.get("virtual_resolution", (800, 600))
    if (
        isinstance(virtual_resolution, (list, tuple))
        and len(virtual_resolution) == 2
    ):
        default_vw, default_vh = (
            int(virtual_resolution[0]),
            int(virtual_resolution[1]),
        )
    else:
        default_vw, default_vh = (800, 600)
    virtual_width = int(_arg_or_default(kwargs, "virtual_width", default_vw))
    virtual_height = int(_arg_or_default(kwargs, "virtual_height", default_vh))

    backend_window = backend_defaults.get("window", {})
    if not isinstance(backend_window, dict):
        backend_window = {}
    window_width = int(
        _arg_or_default(kwargs, "window_width", backend_window.get("width", 960))
    )
    window_height = int(
        _arg_or_default(kwargs, "window_height", backend_window.get("height", 540))
    )
    resizable = bool(backend_window.get("resizable", True))
    base_title = str(backend_window.get("title", EXAMPLE_ID))
    title = f"{base_title} ({backend})"

    renderer = backend_defaults.get("renderer", {})
    if not isinstance(renderer, dict):
        renderer = {}
    background_color = _rgb_or_default(
        renderer.get("background_color"),
        (20, 20, 20),
    )

    enable_profiler = bool(
        _arg_or_default(
            kwargs,
            "enable_profiler",
            engine_defaults.get("enable_profiler", False),
        )
    )
    postfx_defaults = engine_defaults.get("postfx", {})
    if not isinstance(postfx_defaults, dict):
        postfx_defaults = {}
    postfx_enabled = bool(
        _arg_or_default(
            kwargs,
            "postfx_enabled",
            postfx_defaults.get("enabled", False),
        )
    )
    postfx_active = _list_arg(
        _arg_or_default(
            kwargs,
            "postfx_active",
            postfx_defaults.get("active", []),
        )
    )

    discover = scene_defaults.get("discover_packages", [])
    if not isinstance(discover, list) or not discover:
        discover = list(DEFAULT_DISCOVER_PACKAGES)
    else:
        discover = [str(pkg) for pkg in discover if isinstance(pkg, str)]
    initial_scene = str(scene_defaults.get("initial_scene", DEFAULT_SCENE_ID))

    def _engine_config_factory(_backend_impl):
        return EngineConfig(
            fps=fps,
            virtual_resolution=(virtual_width, virtual_height),
            postfx=PostFXConfig(
                enabled=postfx_enabled,
                active=postfx_active,
            ),
            enable_profiler=enable_profiler,
        )

    return ExampleSpec(
        discover_packages=discover,
        initial_scene=initial_scene,
        fps=fps,
        backend_factory=make_backend_factory(
            title=title,
            backend=backend,
            width=window_width,
            height=window_height,
            resizable=resizable,
            background_color=background_color,
        ),
        engine_config_factory=_engine_config_factory,
    )
