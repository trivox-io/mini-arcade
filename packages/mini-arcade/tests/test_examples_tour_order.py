from __future__ import annotations

from pathlib import Path
import sys

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PACKAGE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from mini_arcade.modules.game_runner.processors import (
    ROADMAP_EXAMPLE_ORDER,
    _discover_example_ids,
)


def test_examples_tour_follows_roadmap_order():
    repo_root = Path(__file__).resolve().parents[3]
    examples_dir = repo_root / "examples" / "catalog"

    discovered = _discover_example_ids(examples_dir)
    expected = [
        example_id
        for example_id in ROADMAP_EXAMPLE_ORDER
        if (examples_dir / example_id / "main.py").exists()
    ]

    assert discovered[: len(expected)] == expected
