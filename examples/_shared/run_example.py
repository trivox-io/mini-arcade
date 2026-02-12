"""
Example runner script.
"""

from __future__ import annotations

import sys

# Justification: False positive for import-error; this is the intended way to run examples.
# pylint: disable=import-error
from examples._shared.runner import run_example


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
    if not argv:
        print("Usage: run_example.py <example_id> [args...]")
        return 2
    example_id = argv[0]
    passthrough = argv[1:]  # pylint: disable=unused-variable
    # You can decide how to parse passthrough later; for now forward nothing.
    return run_example(example_id)


if __name__ == "__main__":
    raise SystemExit(main())
