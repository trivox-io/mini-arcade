from __future__ import annotations

from dataclasses import dataclass

from mini_arcade_core.backend.types import Color


@dataclass
class Stroke:
    """
    Simple stroke entity.

    :ivar color: The color of the stroke.
    :ivar thickness: The thickness of the stroke.
    """

    color: Color = (255, 255, 255, 255)
    thickness: float = 1.0


@dataclass
class Fill:
    """
    Simple fill entity.

    :ivar color: The color of the fill.
    """

    color: Color = (255, 255, 255, 255)


@dataclass
class RenderStyle:
    """
    Simple render style entity.

    :ivar stroke: The stroke of the render style.
    :ivar fill: The fill of the render style.
    """

    stroke: Stroke | None = None
    fill: Fill | None = None
