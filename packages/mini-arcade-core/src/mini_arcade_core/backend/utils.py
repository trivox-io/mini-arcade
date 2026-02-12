"""
Configuration and utility functions for the mini arcade native backend.
"""

from __future__ import annotations

from pathlib import Path

from mini_arcade_core.backend.types import (  # pyright: ignore[reportMissingImports]
    Alpha,
    Color,
    ColorRGBA,
)


def alpha_to_u8(alpha: Alpha | None) -> int:
    """
    Convert an alpha value to an 8-bit integer (0-255).

    :param alpha: Alpha value as float [0.0, 1.0] or int [0, 255], or None for opaque.
    :type alpha: Optional[Union[float, int]]
    :return: Alpha as an integer in the range 0-255.
    :rtype: int
    :raises TypeError: If alpha is a bool.
    :raises ValueError: If alpha is out of range.
    """
    if alpha is None:
        return 255
    if isinstance(alpha, bool):
        raise TypeError("alpha must be a float in [0,1], not bool")
    if isinstance(alpha, int):
        if not 0 <= alpha <= 255:
            raise ValueError(f"int alpha must be in [0, 255], got {alpha!r}")
        return alpha

    a = float(alpha)
    if not 0.0 <= a <= 1.0:
        raise ValueError(f"float alpha must be in [0, 1], got {alpha!r}")
    return int(round(a * 255))


def rgba(color: Color) -> ColorRGBA:
    """
    Convert a color tuple to RGBA format.

    :param color: Color as (r,g,b) or (r,g,b,a).
    :type color: Color
    :return: Color as (r,g,b,a) with alpha as 0-255 integer.
    :rtype: ColorRGBA
    """
    if len(color) == 3:
        r, g, b = color
        return int(r), int(g), int(b), 255
    if len(color) == 4:
        r, g, b, a = color
        return int(r), int(g), int(b), alpha_to_u8(a)
    raise ValueError(f"Color must be (r,g,b) or (r,g,b,a), got {color!r}")


def validate_file_exists(path: str) -> str:
    """
    Validate that a file exists at the given path.

    :param path: Path to the file.
    :type path: str
    :return: The original path if the file exists.
    :rtype: str
    :raises FileNotFoundError: If the file does not exist.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(str(p))
    return str(p)
