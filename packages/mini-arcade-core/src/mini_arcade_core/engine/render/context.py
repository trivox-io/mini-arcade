"""
Render context and stats for a single frame render.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mini_arcade_core.engine.render.viewport import ViewportState


@dataclass
class RenderStats:
    """
    Statistics about the rendering process for a single frame.

    :ivar packets (int): Number of render packets processed.
    :ivar ops (int): Number of rendering operations executed.
    :ivar draw_groups (int): Number of draw groups processed.
    :ivar renderables (int): Number of renderable objects processed.
    """

    packets: int = 0
    ops: int = 0
    draw_groups: int = 0  # approx ok
    renderables: int = 0


@dataclass
class RenderContext:
    """
    Context for rendering a single frame.

    :ivar viewport: ViewportState: Current viewport state.
    :ivar debug_overlay: bool: Whether to render debug overlays.
    :ivar frame_ms: float: Time taken to render the frame in milliseconds.
    :ivar stats: RenderStats: Statistics about the rendering process.
    :ivar meta: dict[str, Any]: Additional metadata for rendering.
    """

    viewport: ViewportState
    debug_overlay: bool = False
    frame_ms: float = 0.0
    stats: RenderStats = field(default_factory=RenderStats)
    meta: dict[str, Any] = field(default_factory=dict)
