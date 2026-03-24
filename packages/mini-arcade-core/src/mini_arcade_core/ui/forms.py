"""
Reusable lightweight form helpers for in-game editors.
"""

from __future__ import annotations

from pathlib import Path


def caret_visible(elapsed: float, *, period: float = 0.9) -> bool:
    """
    Return whether a caret should be visible for the current elapsed time.
    """
    if period <= 0.0:
        return True
    phase = float(elapsed) % float(period)
    return phase < (period * 0.5)


def consume_repeat(
    *,
    held: bool,
    pressed: bool,
    timer: float,
    dt: float,
    initial_delay: float = 0.36,
    repeat_delay: float = 0.055,
) -> tuple[bool, float]:
    """
    Return whether an action should repeat this frame for a held key.
    """
    if pressed:
        return True, float(initial_delay)
    if not held:
        return False, 0.0
    next_timer = float(timer) - float(dt)
    if next_timer > 0.0:
        return False, next_timer
    return True, float(repeat_delay)


def open_file_dialog(
    *,
    title: str = "Choose file",
    initial_dir: str | None = None,
    file_types: tuple[tuple[str, str], ...] = (
        ("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.webp"),
        ("All Files", "*.*"),
    ),
) -> str | None:
    """
    Open a native file dialog and return the selected path, if any.
    """
    try:
        # Justification: We want to avoid a hard dependency on tkinter, and this function
        # is only used in a few places, so it's fine to import it here.
        # pylint: disable=import-outside-toplevel
        import tkinter as tk
        from tkinter import filedialog

        # pylint: enable=import-outside-toplevel

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        selected = filedialog.askopenfilename(
            title=title,
            initialdir=initial_dir or str(Path.cwd()),
            filetypes=list(file_types),
        )
        root.destroy()
    except Exception:
        return None
    text = str(selected or "").strip()
    return text or None
