"""
Example: config/engine_config_basics
"""

from __future__ import annotations

from examples._shared.defaults import make_backend_factory
from examples._shared.spec import ExampleSpec
from mini_arcade_core import GameConfig
from mini_arcade_core.engine.game_config import PostFXConfig


def _list_arg(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str):
        return [token.strip() for token in value.split(",") if token.strip()]
    return [str(value)]


def build_example(**kwargs) -> ExampleSpec:
    """
    Build the tutorial spec for engine configuration basics.
    """
    backend = str(kwargs.get("backend", "pygame")).lower().strip()
    fps = int(kwargs.get("fps", 60))
    virtual_width = int(kwargs.get("virtual_width", 800))
    virtual_height = int(kwargs.get("virtual_height", 600))
    window_width = int(kwargs.get("window_width", 960))
    window_height = int(kwargs.get("window_height", 540))
    enable_profiler = bool(kwargs.get("enable_profiler", False))
    postfx_enabled = bool(kwargs.get("postfx_enabled", False))
    postfx_active = _list_arg(kwargs.get("postfx_active"))

    discover = [
        "examples.catalog.config.engine_config_basics",
        "mini_arcade_core.scenes",
    ]

    def _game_config_factory(backend_impl, _registry):
        return GameConfig(
            initial_scene="engine_config_basics",
            fps=fps,
            backend=backend_impl,
            virtual_resolution=(virtual_width, virtual_height),
            postfx=PostFXConfig(
                enabled=postfx_enabled,
                active=postfx_active,
            ),
            enable_profiler=enable_profiler,
        )

    title = f"Example: config/engine_config_basics ({backend})"
    return ExampleSpec(
        discover_packages=discover,
        initial_scene="engine_config_basics",
        fps=fps,
        backend_factory=make_backend_factory(
            title=title,
            backend=backend,
            width=window_width,
            height=window_height,
        ),
        game_config_factory=_game_config_factory,
    )

