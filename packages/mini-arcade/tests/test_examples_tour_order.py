from __future__ import annotations

import os
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PACKAGE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from mini_arcade.modules.game_runner.processors import (
    ROADMAP_EXAMPLE_ORDER,
    ExamplesTourProcessor,
    TargetSpec,
    _build_pythonpath,
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


def test_examples_tour_runs_examples_from_parent_path(
    tmp_path: Path,
    monkeypatch,
):
    examples_dir = tmp_path / "examples" / "catalog"
    example_dir = examples_dir / "scene" / "minimal_scene"
    shared_runner = tmp_path / "examples" / "_shared" / "run_example.py"

    example_dir.mkdir(parents=True)
    shared_runner.parent.mkdir(parents=True)
    (example_dir / "main.py").write_text(
        "def main():\n    return 0\n",
        encoding="utf-8",
    )
    shared_runner.write_text(
        "if __name__ == '__main__':\n    pass\n",
        encoding="utf-8",
    )

    seen: list[tuple[list[str], Path]] = []

    def _fake_run_child_process(
        *, cmd: list[str], cwd: Path, env: dict[str, str]
    ):
        seen.append((cmd, cwd))
        assert "PYTHONPATH" in env
        return (0, False)

    monkeypatch.setattr(
        "mini_arcade.modules.game_runner.processors._run_child_process",
        _fake_run_child_process,
    )

    processor = ExamplesTourProcessor(examples_dir=str(examples_dir))

    assert processor.run() == 0
    assert len(seen) == 1
    assert seen[0][1] == example_dir.resolve()
    assert seen[0][0][2] == "scene/minimal_scene"


def test_build_pythonpath_prefers_workspace_package_sources(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    examples_dir = (
        repo_root / "examples" / "catalog" / "config" / "backend_swap"
    )
    packages_dir = repo_root / "packages"

    (repo_root / "pyproject.toml").write_text(
        "[project]\nname='repo'\n",
        encoding="utf-8",
    )
    examples_dir.mkdir(parents=True)
    (packages_dir / "mini-arcade-core" / "src").mkdir(parents=True)
    (packages_dir / "mini-arcade-pygame-backend" / "src").mkdir(parents=True)
    (packages_dir / "mini-arcade-native-backend" / "src").mkdir(parents=True)

    spec = TargetSpec(
        kind="example",
        target_id="config/backend_swap",
        root_dir=examples_dir,
        entrypoint=repo_root / "examples" / "_shared" / "run_example.py",
        meta={"source_roots": ["src"]},
    )

    parts = _build_pythonpath(spec).split(os.pathsep)

    assert str((packages_dir / "mini-arcade-core" / "src").resolve()) in parts
    assert (
        str((packages_dir / "mini-arcade-pygame-backend" / "src").resolve())
        in parts
    )
    assert (
        str((packages_dir / "mini-arcade-native-backend" / "src").resolve())
        in parts
    )
    assert str(repo_root.resolve()) in parts
