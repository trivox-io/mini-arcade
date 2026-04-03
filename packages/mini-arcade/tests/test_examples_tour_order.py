from __future__ import annotations

import os
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PACKAGE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from mini_arcade.commands.eg.examples_tour import (
    ROADMAP_EXAMPLE_ORDER,
    ExampleTourDiscoverer,
)
from mini_arcade.commands.eg.processors import ExamplesTourProcessor
from mini_arcade.commands.game.processors import (
    GameRunnerProcessor,
    TargetSpec,
    _build_pythonpath,
)


def test_examples_tour_follows_roadmap_order():
    repo_root = Path(__file__).resolve().parents[3]
    examples_dir = repo_root / "examples" / "catalog"

    discovered = ExampleTourDiscoverer(examples_dir).discover_example_ids()
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
        "mini_arcade.commands.eg.processors.run_child_process",
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


def test_examples_tour_returns_nonzero_when_example_fails(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
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

    def _fake_run_child_process(
        *, cmd: list[str], cwd: Path, env: dict[str, str]
    ):
        del cmd, cwd, env
        return (7, False)

    monkeypatch.setattr(
        "mini_arcade.commands.eg.processors.run_child_process",
        _fake_run_child_process,
    )

    processor = ExamplesTourProcessor(examples_dir=str(examples_dir))

    assert processor.run() == 7
    captured = capsys.readouterr().out
    assert "[1/1] Failed: scene/minimal_scene (exit code 7)" in captured
    assert "Examples tour completed: total=1, passed=0, failed=1" in captured


def _write_minimal_game(root: Path, package: str, game_id: str) -> None:
    root.mkdir(parents=True)
    (root / "settings").mkdir()
    (root / "src" / package).mkdir(parents=True)
    (root / "pyproject.toml").write_text(
        "\n".join(
            [
                "[tool.mini-arcade.game]",
                f'id = "{game_id}"',
                'entrypoint = "manage.py"',
                'source_roots = ["src"]',
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / "manage.py").write_text(
        "if __name__ == '__main__':\n    pass\n",
        encoding="utf-8",
    )
    (root / "settings" / "settings.yml").write_text(
        f"game:\n  id: {game_id}\n",
        encoding="utf-8",
    )


def test_game_runner_defaults_to_games_and_sets_settings_env(
    tmp_path: Path,
    monkeypatch,
) -> None:
    game_dir = tmp_path / "games" / "orbit-garden"
    _write_minimal_game(game_dir, "orbit_garden", "orbit-garden")
    monkeypatch.chdir(tmp_path)

    seen: list[tuple[list[str], Path, dict[str, str]]] = []

    def _fake_run_child_process(
        *, cmd: list[str], cwd: Path, env: dict[str, str]
    ):
        seen.append((cmd, cwd, env))
        return (0, False)

    monkeypatch.setattr(
        "mini_arcade.commands.game.processors.run_child_process",
        _fake_run_child_process,
    )

    processor = GameRunnerProcessor(name="orbit-garden", pass_through=[])

    assert processor.run() == 0
    assert len(seen) == 1
    assert seen[0][1] == game_dir.resolve()
    assert seen[0][2]["MINI_ARCADE_CONFIG_PATH"] == str(
        (game_dir / "settings" / "settings.yml").resolve()
    )


def test_game_runner_honors_from_source_override(
    tmp_path: Path,
    monkeypatch,
) -> None:
    default_game = tmp_path / "games" / "orbit-garden"
    custom_parent = tmp_path / "custom-games"
    custom_game = custom_parent / "orbit-garden"
    _write_minimal_game(default_game, "orbit_garden", "orbit-garden")
    _write_minimal_game(custom_game, "orbit_garden", "orbit-garden")
    monkeypatch.chdir(tmp_path)

    seen: list[tuple[list[str], Path, dict[str, str]]] = []

    def _fake_run_child_process(
        *, cmd: list[str], cwd: Path, env: dict[str, str]
    ):
        seen.append((cmd, cwd, env))
        return (0, False)

    monkeypatch.setattr(
        "mini_arcade.commands.game.processors.run_child_process",
        _fake_run_child_process,
    )

    processor = GameRunnerProcessor(
        name="orbit-garden",
        from_source=str(custom_parent),
        pass_through=[],
    )

    assert processor.run() == 0
    assert len(seen) == 1
    assert seen[0][1] == custom_game.resolve()
