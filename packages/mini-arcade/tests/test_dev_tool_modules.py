from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from jinja2 import UndefinedError

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PACKAGE_ROOT / "src"
REPO_ROOT = PACKAGE_ROOT.parents[1]
EXTRA_PATHS = (
    REPO_ROOT,
    SRC_ROOT,
    REPO_ROOT / "packages" / "mini-arcade-core" / "src",
    REPO_ROOT / "packages" / "mini-arcade-pygame-backend" / "src",
    REPO_ROOT / "packages" / "mini-arcade-native-backend" / "src",
)
for path in reversed(EXTRA_PATHS):
    value = str(path)
    if value not in sys.path:
        sys.path.insert(0, value)

import mini_arcade.commands as commands_pkg
from mini_arcade.app import MiniArcadeCLI
from mini_arcade.cli.cli import CLIConfig, GlobalParserBuilder
from mini_arcade.cli.registry import CommandRegistry
from mini_arcade.commands.eg.commands import ExampleRunnerCommand
from mini_arcade.commands.game.commands import (
    GameRunnerCommand,
    ScaffoldGameCommand,
)
from mini_arcade.commands.game.processors import GameScaffoldProcessor
from mini_arcade.commands.shared.scaffold import render_template_tree
from mini_arcade.commands.system_lab.commands import (
    ScaffoldSystemCommand,
    SystemCommand,
)
from mini_arcade.commands.system_lab.processors import (
    SystemRunnerProcessor,
    SystemScaffoldProcessor,
)
from mini_arcade.commands.system_lab.registry import SystemLabRegistry
from mini_arcade.constants import APP, CLI
from mini_arcade.project_launcher import run_project_entrypoint
from mini_arcade.utils.module_loader import load_command_packages


def _build_cli() -> MiniArcadeCLI:
    global_parser = GlobalParserBuilder.build_global_parser(APP.version)
    load_command_packages(
        base_namespace="mini_arcade.commands",
        base_dir=Path(commands_pkg.__file__).parent,
    )
    return MiniArcadeCLI(
        config=CLIConfig(
            app_name=CLI.executable_name,
            description=CLI.description,
            usage=CLI.usage,
            parents=[global_parser],
        )
    )


def test_scaffold_game_command_registers() -> None:
    assert CommandRegistry.contains("game")
    assert CommandRegistry.contains("game-scaffold")
    assert CommandRegistry.contains(ExampleRunnerCommand.name)
    assert CommandRegistry.contains("eg-tour")
    assert CommandRegistry.contains("system")
    assert CommandRegistry.contains("system-scaffold")


def test_cli_parses_runnable_group_commands() -> None:
    cli = _build_cli()

    eg_args = cli.parse_args(["eg", "--id", "scene/minimal_scene"])
    game_args = cli.parse_args(["game", "--name", "pong"])
    system_args = cli.parse_args(
        [
            "system",
            "--module",
            "experiments.procedural_fire_lab.system_lab_case",
            "--list",
        ]
    )

    assert eg_args.id == "scene/minimal_scene"
    assert game_args.name == "pong"
    assert system_args.module == [
        "experiments.procedural_fire_lab.system_lab_case"
    ]


def test_cli_parses_nested_scaffold_subcommands() -> None:
    cli = _build_cli()

    game_args = cli.parse_args(["game", "scaffold", "--id", "laser-garden"])
    system_args = cli.parse_args(["system", "scaffold", "--id", "orbit-lab"])
    eg_args = cli.parse_args(["eg", "tour", "--group", "scene"])

    assert game_args.id == "laser-garden"
    assert system_args.id == "orbit-lab"
    assert eg_args.group == "scene"


def test_render_template_tree_renders_paths_and_strips_jinja_suffix(
    tmp_path: Path,
) -> None:
    files = render_template_tree(
        "game",
        tmp_path,
        {
            "dependency_series": "1.6",
            "game_id": "laser-garden",
            "package": "laser_garden",
            "title": "Laser Garden",
        },
    )

    assert tmp_path / "pyproject.toml" in files
    assert tmp_path / "manage.py" in files
    assert (
        tmp_path
        / "src"
        / "laser_garden"
        / "scenes"
        / "play"
        / "systems"
        / "render.py"
    ) in files
    assert tmp_path / "__init__.py" not in files


def test_render_template_tree_copies_static_files_and_fails_on_missing_variables(
    tmp_path: Path,
) -> None:
    files = render_template_tree(
        "game",
        tmp_path,
        {
            "dependency_series": "1.6",
            "game_id": "laser-garden",
            "package": "laser_garden",
            "title": "Laser Garden",
        },
    )

    assert files[tmp_path / "src" / "laser_garden" / "__init__.py"] == ""
    assert files[tmp_path / "assets" / "sprites" / ".gitkeep"].strip() == ""

    with pytest.raises(UndefinedError):
        render_template_tree(
            "game",
            tmp_path,
            {
                "package": "laser_garden",
            },
        )


def test_game_scaffold_creates_current_project_layout(tmp_path: Path) -> None:
    processor = GameScaffoldProcessor(
        id="laser-garden",
        destination=str(tmp_path),
    )

    assert processor.run() == 0

    root = tmp_path / "laser-garden"
    dependency_series = ".".join(APP.version.split(".")[:2])
    assert (root / "pyproject.toml").exists()
    assert (root / "manage.py").exists()
    assert (root / "settings" / "settings.yml").exists()
    assert (
        root / "src" / "laser_garden" / "scenes" / "play" / "bootstrap.py"
    ).exists()
    assert (
        root / "src" / "laser_garden" / "scenes" / "play" / "pipeline.py"
    ).exists()
    scene_text = (
        root / "src" / "laser_garden" / "scenes" / "play" / "scene.py"
    ).read_text(encoding="utf-8")
    pyproject_text = (root / "pyproject.toml").read_text(encoding="utf-8")
    pipeline_text = (
        root / "src" / "laser_garden" / "scenes" / "play" / "pipeline.py"
    ).read_text(encoding="utf-8")
    assert 'controls_scene_key="play"' in scene_text
    assert "build_play_systems()" in scene_text
    assert "mini-arcade-core~=" + dependency_series in pyproject_text
    assert (
        "from .systems import PlayRenderSystem, PlayRulesSystem"
        in pipeline_text
    )
    assert (
        (root / "src" / "laser_garden" / "scenes" / "menu.py")
        .read_text(encoding="utf-8")
        .startswith("from __future__ import annotations")
    )
    assert (
        (root / "src" / "laser_garden" / "scenes" / "pause.py")
        .read_text(encoding="utf-8")
        .startswith("from __future__ import annotations")
    )
    assert (
        root
        / "src"
        / "laser_garden"
        / "scenes"
        / "play"
        / "systems"
        / "render.py"
    ).exists()
    assert (
        root
        / "src"
        / "laser_garden"
        / "scenes"
        / "play"
        / "systems"
        / "rules.py"
    ).exists()
    assert (root / "assets" / "sprites" / ".gitkeep").exists()
    assert (root / "assets" / "fonts" / ".gitkeep").exists()
    assert (root / "assets" / "sfx" / ".gitkeep").exists()


def test_game_scaffold_command_ignores_global_cli_kwargs(
    tmp_path: Path,
) -> None:
    command = ScaffoldGameCommand()

    assert (
        command.execute(
            id="ball-vs-ball",
            package="bvb",
            title="Ball vs Ball",
            destination=str(tmp_path),
            verbose=1,
        )
        == 0
    )
    assert (tmp_path / "ball-vs-ball" / "manage.py").exists()


def test_game_scaffold_defaults_to_games_directory(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    processor = GameScaffoldProcessor(id="laser-garden")

    assert processor.run() == 0
    assert (tmp_path / "games" / "laser-garden" / "manage.py").exists()


def test_game_scaffold_dry_run_does_not_write_files(
    tmp_path: Path,
    capsys,
) -> None:
    processor = GameScaffoldProcessor(
        id="laser-garden",
        destination=str(tmp_path),
        dry_run=True,
    )

    assert processor.run() == 0
    assert not (tmp_path / "laser-garden").exists()
    assert "laser-garden" in capsys.readouterr().out


def test_system_scaffold_creates_minimal_layout(tmp_path: Path) -> None:
    processor = SystemScaffoldProcessor(
        id="orbit-lab",
        destination=str(tmp_path),
    )

    assert processor.run() == 0

    root = tmp_path / "orbit_lab"
    assert (root / "__init__.py").exists()
    assert (root / "manage.py").exists()
    assert (root / "system_lab_case.py").exists()

    manage_text = (root / "manage.py").read_text(encoding="utf-8")
    case_text = (root / "system_lab_case.py").read_text(encoding="utf-8")
    assert (
        'description="Launch the Orbit Lab experiment directly."'
        in manage_text
    )
    assert 'case="orbit_lab"' in manage_text
    assert '@SystemLabRegistry.implementation("orbit_lab")' in case_text
    assert "BaseSystemLabCase" in case_text
    assert "class OrbitLabSystem" in case_text
    assert 'text="Orbit Lab"' in case_text
    assert "Replace OrbitLabSystem.step() with your experiment." in case_text
    assert "F5 reloads this lab after edits." in case_text


def test_system_scaffold_command_ignores_global_cli_kwargs(
    tmp_path: Path,
) -> None:
    command = ScaffoldSystemCommand()

    assert (
        command.execute(
            id="signal_lab",
            destination=str(tmp_path),
            verbose=1,
        )
        == 0
    )
    assert (tmp_path / "signal_lab" / "manage.py").exists()


def test_system_scaffold_dry_run_does_not_write_files(
    tmp_path: Path,
    capsys,
) -> None:
    processor = SystemScaffoldProcessor(
        id="signal-lab",
        destination=str(tmp_path),
        dry_run=True,
    )

    assert processor.run() == 0
    assert not (tmp_path / "signal_lab").exists()
    output = capsys.readouterr().out
    assert "signal_lab" in output
    assert "experiments.signal_lab.system_lab_case" in output


def test_system_lists_and_runs_registered_case(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    SystemLabRegistry.clear()
    package_dir = tmp_path / "labcases"
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "sample_cases.py").write_text(
        """from mini_arcade.commands.system_lab.registry import BaseSystemLabCase, SystemLabRegistry


class CounterSystem:
    name = "counter_system"

    def step(self, ctx):
        ctx["value"] += 2


@SystemLabRegistry.implementation("counter_case")
class CounterCase(BaseSystemLabCase):
    def build_system(self):
        return CounterSystem()

    def build_context(self):
        return {"value": 1}

    def summarize(self, *, system, ctx, steps):
        return {"value": ctx["value"]}
""",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    assert (
        SystemRunnerProcessor(
            module=["labcases.sample_cases"], list=True
        ).run()
        == 0
    )
    assert "counter_case" in capsys.readouterr().out

    assert (
        SystemRunnerProcessor(
            module=["labcases.sample_cases"],
            case="counter_case",
            steps=3,
            json=True,
        ).run()
        == 0
    )
    output = capsys.readouterr().out
    assert '"case": "counter_case"' in output
    assert '"value": 7' in output


def test_system_command_ignores_global_cli_kwargs(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    SystemLabRegistry.clear()
    package_dir = tmp_path / "labcases"
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "sample_cases.py").write_text(
        """from mini_arcade.commands.system_lab.registry import BaseSystemLabCase, SystemLabRegistry


class CounterSystem:
    def step(self, ctx):
        ctx["value"] += 1


@SystemLabRegistry.implementation("counter_case")
class CounterCase(BaseSystemLabCase):
    def build_system(self):
        return CounterSystem()

    def build_context(self):
        return {"value": 0}
""",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    command = SystemCommand()
    assert (
        command.execute(
            module=["labcases.sample_cases"],
            list=True,
            verbose=2,
        )
        == 0
    )
    assert "counter_case" in capsys.readouterr().out


def test_system_cli_parses_module_without_swallowing_flags() -> None:
    cli = _build_cli()

    args = cli.parse_args(
        [
            "system",
            "--module",
            "experiments.procedural_fire_lab.system_lab_case",
            "--list",
            "--json",
        ]
    )

    assert args.module == ["experiments.procedural_fire_lab.system_lab_case"]
    assert args.list is True
    assert args.json is True


def test_system_cli_parses_visual_backend_override() -> None:
    command = SystemCommand()

    command.validate(
        module=["experiments.procedural_fire_lab.system_lab_case"],
        visual=True,
        backend="native",
    )


def test_system_visual_runner_path(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    SystemLabRegistry.clear()
    package_dir = tmp_path / "labcases_visual"
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "sample_cases.py").write_text(
        """from mini_arcade.commands.system_lab.registry import BaseSystemLabCase, SystemLabRegistry


@SystemLabRegistry.implementation("visual_case")
class VisualCase(BaseSystemLabCase):
    def build_system(self):
        raise RuntimeError("headless path should not be used")

    def build_context(self):
        raise RuntimeError("headless path should not be used")

    def run_visual(self):
        print("visual runner launched")
        return 0
""",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    assert (
        SystemRunnerProcessor(
            module=["labcases_visual.sample_cases"],
            case="visual_case",
            visual=True,
        ).run()
        == 0
    )
    assert "visual runner launched" in capsys.readouterr().out


def test_system_visual_runner_auto_selects_single_case(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    SystemLabRegistry.clear()
    package_dir = tmp_path / "labcases_visual_auto"
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "sample_cases.py").write_text(
        """from mini_arcade.commands.system_lab.registry import BaseSystemLabCase, SystemLabRegistry


@SystemLabRegistry.implementation("visual_case")
class VisualCase(BaseSystemLabCase):
    def build_system(self):
        raise RuntimeError("headless path should not be used")

    def build_context(self):
        raise RuntimeError("headless path should not be used")

    def run_visual(self):
        print("visual auto runner launched")
        return 0
""",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    assert (
        SystemRunnerProcessor(
            module=["labcases_visual_auto.sample_cases"],
            visual=True,
        ).run()
        == 0
    )
    assert "visual auto runner launched" in capsys.readouterr().out


def test_system_default_visual_runner_uses_builtin_lab(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    SystemLabRegistry.clear()
    package_dir = tmp_path / "labcases_builtin_visual"
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "sample_cases.py").write_text(
        """from dataclasses import dataclass

from mini_arcade.commands.system_lab.registry import BaseSystemLabCase, SystemLabRegistry


class DummySystem:
    name = "dummy_visual_system"

    def step(self, ctx):
        ctx.world["value"] += 1


@dataclass
class DummyContext:
    world: dict


@SystemLabRegistry.implementation("visual_case")
class VisualCase(BaseSystemLabCase):
    visual_title = "Builtin Visual"

    def build_system(self):
        return DummySystem()

    def build_context(self):
        return DummyContext(world={"value": 0})
""",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    captured: dict[str, object] = {}

    def fake_run(
        case,
        spec,
        *,
        module_names=(),
        backend_provider_override=None,
    ):
        captured["case_name"] = case.__class__.__name__
        captured["spec"] = spec
        captured["module_names"] = module_names
        captured["backend_provider_override"] = backend_provider_override
        print(f"builtin visual: {spec.title}")
        return 0

    monkeypatch.setattr(
        "mini_arcade.commands.system_lab.visual_runner.run_system_lab_visual_case",
        fake_run,
    )

    assert (
        SystemRunnerProcessor(
            module=["labcases_builtin_visual.sample_cases"],
            case="visual_case",
            visual=True,
        ).run()
        == 0
    )
    assert "builtin visual: Builtin Visual" in capsys.readouterr().out
    assert captured["case_name"] == "VisualCase"
    assert getattr(captured["spec"], "title") == "Builtin Visual"
    assert getattr(captured["spec"], "debug_overlay_enabled") is True
    assert getattr(captured["spec"], "debug_overlay_start_visible") is False
    assert getattr(captured["spec"], "hot_reload_enabled") is True
    assert getattr(captured["spec"], "hot_reload_key") == "F5"
    assert captured["module_names"] == (
        "labcases_builtin_visual.sample_cases",
    )
    assert captured["backend_provider_override"] is None


def test_system_visual_backend_override_reaches_visual_runner(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    SystemLabRegistry.clear()
    package_dir = tmp_path / "labcases_backend_override"
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "sample_cases.py").write_text(
        """from dataclasses import dataclass

from mini_arcade.commands.system_lab.registry import BaseSystemLabCase, SystemLabRegistry


class DummySystem:
    name = "dummy_visual_system"

    def step(self, ctx):
        ctx.world["value"] += 1


@dataclass
class DummyContext:
    world: dict


@SystemLabRegistry.implementation("visual_case")
class VisualCase(BaseSystemLabCase):
    def build_system(self):
        return DummySystem()

    def build_context(self):
        return DummyContext(world={"value": 0})
""",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    captured: dict[str, object] = {}

    def fake_run(
        case,
        spec,
        *,
        module_names=(),
        backend_provider_override=None,
    ):
        del case
        del spec
        captured["module_names"] = module_names
        captured["backend_provider_override"] = backend_provider_override
        print("backend override captured")
        return 0

    monkeypatch.setattr(
        "mini_arcade.commands.system_lab.visual_runner.run_system_lab_visual_case",
        fake_run,
    )

    assert (
        SystemRunnerProcessor(
            module=["labcases_backend_override.sample_cases"],
            case="visual_case",
            visual=True,
            backend="native",
        ).run()
        == 0
    )
    assert "backend override captured" in capsys.readouterr().out
    assert captured["module_names"] == (
        "labcases_backend_override.sample_cases",
    )
    assert captured["backend_provider_override"] == "native"


def test_system_visual_runner_discovers_watch_paths(
    tmp_path: Path,
    monkeypatch,
) -> None:
    package_dir = tmp_path / "labcases_reload"
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "helpers.py").write_text(
        "VALUE = 1\n",
        encoding="utf-8",
    )
    (package_dir / "sample_cases.py").write_text(
        "from .helpers import VALUE\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    importlib.import_module("labcases_reload.sample_cases")

    from mini_arcade.commands.system_lab.visual_runner import (
        _discover_watch_paths,
    )

    watch_paths = _discover_watch_paths(("labcases_reload.sample_cases",))

    assert package_dir / "sample_cases.py" in watch_paths
    assert package_dir / "helpers.py" in watch_paths


def test_procedural_fire_lab_case_runs_headless(capsys) -> None:
    SystemLabRegistry.clear()

    assert (
        SystemRunnerProcessor(
            module=["experiments.procedural_fire_lab.system_lab_case"],
            case="procedural_fire_stats",
            steps=2,
            json=True,
        ).run()
        == 0
    )
    output = capsys.readouterr().out
    assert '"case": "procedural_fire_stats"' in output
    assert '"particle_count":' in output


def test_procedural_fire_lab_visual_spec_uses_live_tick_context() -> None:
    from experiments.procedural_fire_lab.system_lab_case import (
        FireLabTickContext,
        ProceduralFireStatsCase,
    )

    spec = ProceduralFireStatsCase().build_visual_spec()

    assert spec is not None
    assert spec.tick_context_type is FireLabTickContext


def test_bouncing_balls_case_runs_headless(capsys) -> None:
    SystemLabRegistry.clear()

    assert (
        SystemRunnerProcessor(
            module=["experiments.bouncing_balls.system_lab_case"],
            case="bouncing_balls",
            steps=3,
            json=True,
        ).run()
        == 0
    )
    output = capsys.readouterr().out
    assert '"case": "bouncing_balls"' in output
    assert '"ball_count": 2' in output
    assert '"ball_a":' in output
    assert '"ball_b":' in output


def test_bounce_box_stress_case_runs_headless(capsys) -> None:
    SystemLabRegistry.clear()

    assert (
        SystemRunnerProcessor(
            module=["experiments.bounce_box_stress_lab.system_lab_case"],
            case="bounce_box_stress",
            steps=3,
            json=True,
        ).run()
        == 0
    )
    output = capsys.readouterr().out
    assert '"case": "bounce_box_stress"' in output
    assert '"ball_count": 4' in output
    assert '"fps":' in output
    assert '"total_collisions":' in output


def test_camera_lab_case_runs_headless(capsys) -> None:
    SystemLabRegistry.clear()

    assert (
        SystemRunnerProcessor(
            module=["experiments.camera_lab.system_lab_case"],
            case="camera_lab",
            steps=3,
            json=True,
        ).run()
        == 0
    )
    output = capsys.readouterr().out
    assert '"case": "camera_lab"' in output
    assert '"camera_center":' in output
    assert '"camera_zoom":' in output


def test_ball_vs_ball_combat_lab_runs_headless(capsys) -> None:
    SystemLabRegistry.clear()

    assert (
        SystemRunnerProcessor(
            module=["experiments.ball_vs_ball_combat.system_lab_case"],
            case="ball_vs_ball_combat",
            steps=240,
            json=True,
        ).run()
        == 0
    )
    output = capsys.readouterr().out
    assert '"case": "ball_vs_ball_combat"' in output
    assert '"ball_count": 2' in output
    assert '"damage_events":' in output


def test_ball_vs_ball_powerup_sandbox_runs_headless(capsys) -> None:
    SystemLabRegistry.clear()

    assert (
        SystemRunnerProcessor(
            module=[
                "experiments.ball_vs_ball_powerup_sandbox.system_lab_case"
            ],
            case="ball_vs_ball_powerup_sandbox",
            steps=120,
            json=True,
        ).run()
        == 0
    )
    output = capsys.readouterr().out
    assert '"case": "ball_vs_ball_powerup_sandbox"' in output
    assert '"selected_powerup": "cure"' in output
    assert '"placement_count": 0' in output


def test_ball_vs_ball_powerup_sandbox_spawned_pickup_is_indexed() -> None:
    from experiments.ball_vs_ball_powerup_sandbox.system_lab_case import (
        BallVsBallPowerupSandboxContext,
        _entity_actual_center,
        _spawn_selected_pickup_at,
        build_powerup_sandbox_world,
    )
    from mini_arcade_core.engine.commands import CommandQueue
    from mini_arcade_core.runtime.input_frame import InputFrame

    world = build_powerup_sandbox_world(viewport=(540.0, 960.0))
    ctx = BallVsBallPowerupSandboxContext(
        input_frame=InputFrame(frame_index=0, dt=1.0 / 60.0),
        dt=1.0 / 60.0,
        world=world,
        commands=CommandQueue(),
    )
    ball = world.fighter("ball_a")
    assert ball is not None
    x, y = _entity_actual_center(ball)

    assert _spawn_selected_pickup_at(ctx, x=x, y=y) is True
    assert len(world.pickups()) == 1


def test_knockout_bracket_seed_lab_runs_headless(capsys) -> None:
    SystemLabRegistry.clear()

    assert (
        SystemRunnerProcessor(
            module=["experiments.knockout_bracket_seed_lab.system_lab_case"],
            case="knockout_bracket_seed",
            steps=1,
            json=True,
        ).run()
        == 0
    )
    output = capsys.readouterr().out
    assert '"case": "knockout_bracket_seed"' in output
    assert '"round_count": 4' in output
    assert '"entrant_count": 16' in output


def test_knockout_bracket_progress_lab_runs_headless(capsys) -> None:
    SystemLabRegistry.clear()

    assert (
        SystemRunnerProcessor(
            module=[
                "experiments.knockout_bracket_progress_lab.system_lab_case"
            ],
            case="knockout_bracket_progress",
            steps=1,
            json=True,
        ).run()
        == 0
    )
    output = capsys.readouterr().out
    assert '"case": "knockout_bracket_progress"' in output
    assert '"playable_matches": 8' in output


def test_knockout_bracket_progress_selection_uses_next_playable_match() -> (
    None
):
    from experiments.knockout_bracket_common import (
        BracketLabIntent,
        BracketProgressSelectionSystem,
        build_bracket_world,
        build_progress_system,
        build_seed_system,
    )
    from mini_arcade_core.engine.commands import CommandQueue
    from mini_arcade_core.runtime.input_frame import InputFrame

    ctx = SimpleNamespace(
        input_frame=InputFrame(frame_index=0, dt=1.0 / 60.0),
        dt=1.0 / 60.0,
        world=build_bracket_world(
            title="Knockout Bracket Progress Lab",
            subtitle="Advance the next playable match and propagate winners through the tree.",
            progress_mode=True,
            progressive_mode=True,
        ),
        commands=CommandQueue(),
        intent=BracketLabIntent(),
    )

    build_seed_system().step(ctx)
    ctx.world.selected_playable_index = 99
    BracketProgressSelectionSystem().step(ctx)
    assert ctx.world.pending_result is None
    assert ctx.world.selected_playable_index == 0

    playable = [
        match
        for round_matches in ctx.world.bracket.rounds
        for match in round_matches
        if match.playable
    ]
    for match in playable[:-1]:
        ctx.world.pending_result = SimpleNamespace(
            match_id=match.id,
            winner_id=match.entrant_a_id,
        )
        build_progress_system().step(ctx)

    BracketProgressSelectionSystem().step(ctx)
    assert ctx.world.selected_playable_index == 0


def test_load_command_packages_skips_non_command_modules(
    tmp_path: Path,
    monkeypatch,
) -> None:
    root = tmp_path / "demo_pkg"
    modules_dir = root / "commands"
    modules_dir.mkdir(parents=True)
    (root / "__init__.py").write_text("", encoding="utf-8")
    (modules_dir / "__init__.py").write_text("", encoding="utf-8")

    heavy_pkg = modules_dir / "heavy_only"
    heavy_pkg.mkdir()
    (heavy_pkg / "__init__.py").write_text(
        'raise RuntimeError("should not import heavy_only")',
        encoding="utf-8",
    )

    light_pkg = modules_dir / "light_cmd"
    light_pkg.mkdir()
    (light_pkg / "__init__.py").write_text("", encoding="utf-8")
    (light_pkg / "commands.py").write_text(
        """from mini_arcade.cli.base_command import BaseCommand
from mini_arcade.cli.registry import CommandRegistry


@CommandRegistry.implementation("temp-light-cmd")
class TempLightCommand(BaseCommand):
    name = "temp-light-cmd"

    def _execute(self, **kwargs):
        return 0
""",
        encoding="utf-8",
    )

    monkeypatch.syspath_prepend(str(tmp_path))
    loaded = load_command_packages(
        base_namespace="demo_pkg.commands",
        base_dir=modules_dir,
    )

    assert [pkg.import_name for pkg in loaded] == [
        "demo_pkg.commands.light_cmd"
    ]
    assert CommandRegistry.contains("temp-light-cmd")


def test_project_launcher_runs_local_entrypoint_when_no_args() -> None:
    seen: list[str] = []

    def _local_run():
        seen.append("ran")
        return None

    assert run_project_entrypoint(_local_run, argv=[]) == 0
    assert seen == ["ran"]


def test_project_launcher_dispatches_to_cli_when_args_present(
    monkeypatch,
) -> None:
    captured: dict[str, object] = {}

    def _fake_cli_main(argv, *, extra_command_modules=()):
        captured["argv"] = list(argv)
        captured["extra_command_modules"] = tuple(extra_command_modules)

    monkeypatch.setattr("mini_arcade.main.main", _fake_cli_main)

    assert (
        run_project_entrypoint(
            lambda: captured.setdefault("local", True),
            argv=["eg", "tour"],
            extra_command_modules=("ballistic.commands",),
        )
        == 0
    )
    assert captured["argv"] == ["eg", "tour"]
    assert captured["extra_command_modules"] == ("ballistic.commands",)
    assert "local" not in captured
