"""
Example runner script.
"""

from __future__ import annotations

import argparse
import sys

# Justification: False positive for import-error; this is the intended way to run examples.
# pylint: disable=import-error
from examples._shared.runner import run_example


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run_example.py",
        description=(
            "Run a grouped example id (e.g. config/engine_config_basics)."
        ),
    )
    parser.add_argument("example_id", help="Grouped example id")
    parser.add_argument(
        "--backend",
        choices=["pygame", "native"],
        default=None,
        help="Backend override for examples that support backend selection.",
    )
    parser.add_argument("--fps", type=int, default=None)
    parser.add_argument("--virtual-width", type=int, default=None)
    parser.add_argument("--virtual-height", type=int, default=None)
    parser.add_argument("--window-width", type=int, default=None)
    parser.add_argument("--window-height", type=int, default=None)
    parser.add_argument(
        "--enable-profiler",
        action="store_true",
        default=None,
        help="Enable frame profiling if supported by example config.",
    )
    parser.add_argument(
        "--postfx-enabled",
        action="store_true",
        default=None,
        help="Enable postfx stack by default.",
    )
    parser.add_argument(
        "--postfx-active",
        default=None,
        help="Comma-separated postfx ids, e.g. crt,vignette_noise",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """
    Main entry point for running examples.

    :param argv: Optional list of command-line arguments (excluding script name)
    :type argv: list[str] | None
    :return: Exit code (0 for success, non-zero for failure)
    :rtype: int
    :raises ExampleLoadError: If there is an error loading the example or its spec
    """
    argv = sys.argv[1:] if argv is None else argv
    args = _parser().parse_args(argv)

    kwargs: dict[str, object] = {}
    if args.backend is not None:
        kwargs["backend"] = args.backend
    if args.fps is not None:
        kwargs["fps"] = args.fps
    if args.virtual_width is not None:
        kwargs["virtual_width"] = args.virtual_width
    if args.virtual_height is not None:
        kwargs["virtual_height"] = args.virtual_height
    if args.window_width is not None:
        kwargs["window_width"] = args.window_width
    if args.window_height is not None:
        kwargs["window_height"] = args.window_height
    if args.enable_profiler is not None:
        kwargs["enable_profiler"] = args.enable_profiler
    if args.postfx_enabled is not None:
        kwargs["postfx_enabled"] = args.postfx_enabled
    if args.postfx_active:
        kwargs["postfx_active"] = [
            token.strip()
            for token in str(args.postfx_active).split(",")
            if token.strip()
        ]

    return run_example(args.example_id, **kwargs)


if __name__ == "__main__":
    raise SystemExit(main())
