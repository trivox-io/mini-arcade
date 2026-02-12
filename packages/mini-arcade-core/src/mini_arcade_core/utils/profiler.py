"""
Game core module defining the Game class and configuration.
"""

from __future__ import annotations

import enum
import logging
from dataclasses import dataclass, field
from time import perf_counter
from typing import Dict, Iterable, Mapping

perf_logger = logging.getLogger("mini-arcade-core.perf")


class Ansi(enum.Enum):
    """
    ANSI escape codes for terminal text formatting.

    cvar RESET (str): Reset all formatting.
    cvar BOLD (str): Bold text.
    cvar DIM (str): Dim text.
    cvar RED (str): Red text.
    cvar GREEN (str): Green text.
    cvar YELLOW (str): Yellow text.
    cvar CYAN (str): Cyan text.
    cvar MAGENTA (str): Magenta text.
    cvar WHITE (str): White text.
    """

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    WHITE = "\033[97m"


def _c(text: str, *codes: str) -> str:
    """Convenience function to wrap text with ANSI codes."""
    return "".join(codes) + text + Ansi.RESET.value


@dataclass(frozen=True)
class FrameTimingReport:
    """
    Report of frame timing data.

    :ivar frame_index (int): Index of the frame.
    :ivar diffs_ms (Dict[str, float]): Dictionary of time differences in milliseconds.
    :ivar total_ms (float): Total time in milliseconds.
    :ivar budget_ms (float): Frame budget in milliseconds.
    """

    frame_index: int
    diffs_ms: Dict[str, float]
    total_ms: float
    budget_ms: float


@dataclass(frozen=True)
class FrameTimingFormatter:
    """
    Formats a FrameTimingReport into a colored, multi-line table string.
    Keeps FrameTimer lean and avoids pylint complexity in the timer itself.

    :ivar target_fps (int): Target frames per second for budget calculation.
    :ivar top_n (int): Number of top time-consuming segments to display.
    :ivar min_ms (float): Minimum time in milliseconds to include in the top list.
    :ivar phases (tuple[tuple[str, str], ...]): Tuples of (display name, mark key)
        for table columns.
    """

    target_fps: int = 60
    top_n: int = 6
    min_ms: float = 0.05

    # These are the “headline” segments you want as columns.
    phases: tuple[tuple[str, str], ...] = (
        ("events", "frame_start->events_polled"),
        ("input", "events_polled->input_built"),
        ("tick", "tick_start->tick_end"),
        ("render", "render_start->render_done"),
        ("sleep", "sleep_start->sleep_end"),
    )

    def make_report(
        self, frame_index: int, diffs_ms: Dict[str, float]
    ) -> FrameTimingReport:
        """
        Create a FrameTimingReport from the given diffs.

        :param frame_index: Index of the frame.
        :type frame_index: int
        :param diffs_ms: Dictionary of time differences in milliseconds.
        :type diffs_ms: Dict[str, float]
        :return: FrameTimingReport instance.
        :rtype: FrameTimingReport
        """
        total = sum(diffs_ms.values()) if diffs_ms else 0.0
        budget = (1000.0 / self.target_fps) if self.target_fps > 0 else 0.0
        return FrameTimingReport(
            frame_index=frame_index,
            diffs_ms=diffs_ms,
            total_ms=total,
            budget_ms=budget,
        )

    def format(self, report: FrameTimingReport) -> str:
        """
        Format the FrameTimingReport into a colored string.

        :param report: FrameTimingReport instance.
        :type report: FrameTimingReport
        :return: Formatted string.
        :rtype: str
        """
        header = self._format_header(report)
        table = self._format_table(report.diffs_ms)
        top = self._format_top(report.diffs_ms)
        return f"{header}\n{table}\n{top}\n"

    def _format_header(self, report: FrameTimingReport) -> str:
        over = report.budget_ms > 0 and report.total_ms > report.budget_ms
        status = (
            _c("OVER", Ansi.BOLD.value, Ansi.RED.value)
            if over
            else _c("OK", Ansi.BOLD.value, Ansi.GREEN.value)
        )

        frame = _c(
            f"[Frame {report.frame_index}]", Ansi.BOLD.value, Ansi.WHITE.value
        )
        total = _c(
            f"{report.total_ms:.2f}ms", Ansi.BOLD.value, Ansi.WHITE.value
        )
        budget = _c(f"{report.budget_ms:.2f}ms", Ansi.DIM.value)
        dim = Ansi.DIM.value

        return (
            f"{frame} {_c('total', dim)}={total} "
            f"{_c('budget', dim)}={budget} {_c('status', dim)}={status}"
        )

    def _format_table(self, diffs: Mapping[str, float]) -> str:
        # Header line
        headers = [name for name, _ in self.phases]
        line_h = self._pipe_row((_c(h, Ansi.DIM.value) for h in headers))

        # Values line
        values = [diffs.get(key, 0.0) for _, key in self.phases]
        line_v = self._pipe_row(self._color_values(values))

        return f"{line_h}\n{line_v}"

    def _color_values(self, values: Iterable[float]) -> list[str]:
        # Keep coloring policy centralized and easy to tweak.
        # events/input: cyan, tick: yellow, render: magenta, sleep: green
        colors = [
            Ansi.CYAN.value,
            Ansi.CYAN.value,
            Ansi.YELLOW.value,
            Ansi.MAGENTA.value,
            Ansi.GREEN.value,
        ]
        out: list[str] = []
        for v, col in zip(values, colors):
            out.append(_c(f"{v:6.2f}", col))
        return out

    def _format_top(self, diffs: Mapping[str, float]) -> str:
        dim = Ansi.DIM.value
        items = [
            (k, float(v)) for k, v in diffs.items() if float(v) >= self.min_ms
        ]
        items.sort(key=lambda kv: kv[1], reverse=True)
        items = items[: self.top_n]

        if not items:
            return f"{_c('top:', dim)} (none >= {self.min_ms:.2f}ms)"

        top_str = ", ".join(f"{k}:{v:.2f}ms" for k, v in items)
        return f"{_c('top:', dim)} {top_str}"

    @staticmethod
    def _pipe_row(cells: Iterable[str]) -> str:
        # Keeps lines short and avoids long f-strings.
        return " | ".join(cells)


@dataclass
class FrameTimerConfig:
    """
    Configuration for FrameTimer.

    :ivar enabled (bool): Whether timing is enabled.
    :ivar report_every (int): Number of frames between reports.
    """

    enabled: bool = False
    report_every: int = 60


@dataclass
class FrameTimer:
    """
    Simple frame timer for marking and reporting time intervals.

    :ivar config (FrameTimerConfig): Configuration for the timer.
    :ivar formatter (FrameTimingFormatter): Formatter for timing reports.
    :ivar marks (Dict[str, float]): Recorded time marks.
    """

    config: FrameTimerConfig = field(default_factory=FrameTimerConfig)
    formatter: FrameTimingFormatter = field(
        default_factory=FrameTimingFormatter
    )
    marks: Dict[str, float] = field(default_factory=dict)

    def clear(self):
        """Clear all recorded marks."""
        if not self.config.enabled:
            return
        self.marks.clear()

    def mark(self, name: str):
        """
        Record a time mark with the given name.

        :param name: Name of the mark.
        :type name: str
        """
        if not self.config.enabled:
            return
        self.marks[name] = perf_counter()

    def report_ms(self) -> Dict[str, float]:
        """
        Returns diffs between consecutive marks in insertion order.

        :return: Dictionary mapping "start->end" to time difference in milliseconds.
        :rtype: Dict[str, float]
        """
        if not self.config.enabled:
            return {}
        keys = list(self.marks.keys())
        out: Dict[str, float] = {}
        for a, b in zip(keys, keys[1:]):
            out[f"{a}->{b}"] = (self.marks[b] - self.marks[a]) * 1000.0
        return out

    def should_report(self, frame_index: int) -> bool:
        """
        Determine if a report should be emitted for the given frame index.

        :param frame_index: Current frame index.
        :type frame_index: int
        :return: True if a report should be emitted, False otherwise.
        :rtype: bool
        """
        return (
            self.config.enabled
            and self.config.report_every > 0
            and frame_index > 0
            and (frame_index % self.config.report_every == 0)
        )

    def emit(self, frame_index: int):
        """
        Emit a timing report to the performance logger.

        :param frame_index: Current frame index.
        :type frame_index: int
        """
        if not self.config.enabled:
            return
        diffs = self.report_ms()
        report = self.formatter.make_report(frame_index, diffs)
        perf_logger.info(self.formatter.format(report))
