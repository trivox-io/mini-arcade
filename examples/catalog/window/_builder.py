"""
Shared example builder helpers for window tutorials.
"""

from __future__ import annotations

from typing import Any

from mini_arcade.modules.settings import Settings
from mini_arcade_core import EngineConfig
from mini_arcade_core.engine.engine_config import PostFXConfig

from examples._shared.defaults import make_backend_factory
from examples._shared.spec import ExampleSpec


def _arg_or_default(kwargs: dict[str, Any], key: str, default: Any) -> Any:
    value = kwargs.get(key, default)
    return default if value is None else value


def _list_arg(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str):
        return [token.strip() for token in value.split(",") if token.strip()]
    return [str(value)]


def _rgb_or_default(
    value: object, default: tuple[int, int, int]
) -> tuple[int, int, int]:
    if isinstance(value, (list, tuple)) and len(value) >= 3:
        return (int(value[0]), int(value[1]), int(value[2]))
    return default


def _virtual_resolution(value: object) -> tuple[int, int]:
    if isinstance(value, (list, tuple)) and len(value) == 2:
        return (int(value[0]), int(value[1]))
    return (800, 600)


def build_window_example(
    *,
    example_id: str,
    default_scene_id: str,
    default_discover_package: str,
    kwargs: dict[str, Any],
    default_background_color: tuple[int, int, int],
) -> ExampleSpec:
    """
    Build ExampleSpec using shared window tutorial conventions.
    """
    settings = Settings.for_example(example_id, required=False)
    engine_defaults = settings.engine_config_defaults()
    scene_defaults = settings.scene_defaults()
    backend_defaults = settings.backend_defaults(resolve_paths=True)

    backend = (
        str(
            _arg_or_default(
                kwargs,
                "backend",
                backend_defaults.get("provider", "pygame"),
            )
        )
        .lower()
        .strip()
    )

    fps = int(_arg_or_default(kwargs, "fps", engine_defaults.get("fps", 60)))
    default_vw, default_vh = _virtual_resolution(
        engine_defaults.get("virtual_resolution", (800, 600))
    )
    virtual_width = int(_arg_or_default(kwargs, "virtual_width", default_vw))
    virtual_height = int(_arg_or_default(kwargs, "virtual_height", default_vh))

    backend_window = backend_defaults.get("window", {})
    if not isinstance(backend_window, dict):
        backend_window = {}
    window_width = int(
        _arg_or_default(
            kwargs, "window_width", backend_window.get("width", 960)
        )
    )
    window_height = int(
        _arg_or_default(
            kwargs, "window_height", backend_window.get("height", 540)
        )
    )
    resizable = bool(backend_window.get("resizable", True))
    title_base = (
        str(backend_window.get("title", example_id)).strip() or example_id
    )
    title = f"{title_base} ({backend})"

    renderer = backend_defaults.get("renderer", {})
    if not isinstance(renderer, dict):
        renderer = {}
    background_color = _rgb_or_default(
        renderer.get("background_color"),
        default_background_color,
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
        discover = [default_discover_package, "mini_arcade_core.scenes"]
    else:
        discover = [str(pkg) for pkg in discover if isinstance(pkg, str)]
    initial_scene = str(scene_defaults.get("initial_scene", default_scene_id))

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
