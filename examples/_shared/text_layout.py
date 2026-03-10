"""
Shared text layout helpers for tutorial examples.
"""

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade_core.backend.backend import Backend


@dataclass(frozen=True)
class TextBlockLayout:
    """
    Resolved layout metrics for a simple multi-line text block.
    """

    font_size: int
    line_height: int
    max_width: int
    total_height: int


def _measure_lines(
    backend: Backend,
    lines: list[str],
    *,
    font_size: int,
    line_gap: int,
) -> TextBlockLayout:
    sample_text = "Ag"
    max_width = 0
    line_box_height = 0

    for line in lines:
        measured_text = line if line else sample_text
        measured_width, measured_height = backend.text.measure(
            measured_text,
            font_size=font_size,
        )
        if line:
            max_width = max(max_width, measured_width)
        line_box_height = max(line_box_height, measured_height)

    line_height = line_box_height + line_gap
    total_height = (line_box_height * len(lines)) + (
        line_gap * max(0, len(lines) - 1)
    )
    return TextBlockLayout(
        font_size=font_size,
        line_height=line_height,
        max_width=max_width,
        total_height=total_height,
    )


def fit_text_block(
    backend: Backend,
    lines: list[str],
    *,
    max_width: int,
    max_height: int,
    preferred_font_size: int = 18,
    min_font_size: int = 8,
) -> TextBlockLayout:
    """
    Find the largest font size that keeps a text block inside bounds.
    """
    if not lines:
        return TextBlockLayout(
            font_size=preferred_font_size,
            line_height=preferred_font_size,
            max_width=0,
            total_height=0,
        )

    best_layout: TextBlockLayout | None = None
    for font_size in range(preferred_font_size, min_font_size - 1, -1):
        line_gap = max(2, font_size // 6)
        layout = _measure_lines(
            backend,
            lines,
            font_size=font_size,
            line_gap=line_gap,
        )
        best_layout = layout
        if layout.max_width <= max_width and layout.total_height <= max_height:
            return layout

    if best_layout is None:
        raise ValueError("Expected at least one layout candidate")
    return best_layout


def draw_text_block(
    backend: Backend,
    *,
    x: int,
    y: int,
    lines: list[str],
    layout: TextBlockLayout,
    color=(230, 230, 236),
):
    """
    Draw a pre-measured text block line by line.
    """
    cursor_y = y
    for line in lines:
        backend.text.draw(
            x,
            cursor_y,
            line,
            color=color,
            font_size=layout.font_size,
        )
        cursor_y += layout.line_height
