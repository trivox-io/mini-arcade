"""
Types used in the backend module.
"""

from __future__ import annotations

from typing import Tuple, Union

ColorRGB = Tuple[int, int, int]
ColorRGBA = Tuple[int, int, int, int]

Color = Union[ColorRGB, ColorRGBA]
Alpha = Union[float, int]
