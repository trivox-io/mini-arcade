"""
Specification for example modules.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional, Sequence

from mini_arcade_core import (  # type: ignore[import-not-found]
    EngineConfig,
)


@dataclass(frozen=True)
class ExampleSpec:
    """
    Contract returned by each example's build_example().

    The shared runner will:
        - discover scenes from `discover_packages`
        - build backend via `backend_factory`
        - build EngineConfig and call run_game(...)

    :ivar discover_packages: Sequence[str] - List of packages to discover scenes from
    :ivar initial_scene: str - Name of the initial scene to run
    :ivar fps: int - Target frames per second for the game loop
    :ivar backend_factory: Callable[[], Any] - Factory function to create the game backend
    :ivar engine_config_factory: Optional[Callable[[Any], EngineConfig]]
        - Optional factory function to create an EngineConfig instance
    """

    # Scene discovery
    discover_packages: Sequence[str]

    # Game run configuration
    initial_scene: str
    fps: int

    # Backend creation hook
    backend_factory: Callable[[], Any]

    # Optional config object hook (if you ever want to build EngineConfig differently)
    engine_config_factory: Optional[Callable[[Any], EngineConfig]] = None
