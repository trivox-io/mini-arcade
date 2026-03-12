from __future__ import annotations

from pathlib import Path
import sys

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PACKAGE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from mini_arcade.cli.registry import CommandRegistry
from mini_arcade.cli.cli import CLIConfig, GlobalParserBuilder
from mini_arcade.app import MiniArcadeCLI
from mini_arcade.constants import APP, CLI
from mini_arcade.modules.game_scaffold.commands import ScaffoldGameCommand
from mini_arcade.modules.game_scaffold.processors import GameScaffoldProcessor
from mini_arcade.modules.system_lab.commands import SystemLabCommand
from mini_arcade.modules.system_lab.processors import SystemLabProcessor
from mini_arcade.modules.system_lab.registry import SystemLabRegistry
from mini_arcade.utils.module_loader import load_command_packages
import mini_arcade.modules as commands_pkg


def _build_cli() -> MiniArcadeCLI:
    global_parser = GlobalParserBuilder.build_global_parser(APP.version)
    load_command_packages(
        base_namespace="mini_arcade.modules",
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
    assert CommandRegistry.contains(ScaffoldGameCommand.name)
    assert CommandRegistry.contains(SystemLabCommand.name)


def test_game_scaffold_creates_current_project_layout(tmp_path: Path) -> None:
    processor = GameScaffoldProcessor(
        game_id="laser-garden",
        destination=str(tmp_path),
    )

    assert processor.run() == 0

    root = tmp_path / "laser-garden"
    assert (root / "manage.py").exists()
    assert (root / "settings" / "settings.yml").exists()
    assert (
        root
        / "src"
        / "laser_garden"
        / "scenes"
        / "play"
        / "bootstrap.py"
    ).exists()
    assert (
        root
        / "src"
        / "laser_garden"
        / "scenes"
        / "play"
        / "pipeline.py"
    ).exists()
    scene_text = (
        root
        / "src"
        / "laser_garden"
        / "scenes"
        / "play"
        / "scene.py"
    ).read_text(encoding="utf-8")
    assert 'controls_scene_key="play"' in scene_text
    assert "build_play_systems()" in scene_text
    assert (
        root / "src" / "laser_garden" / "scenes" / "menu.py"
    ).read_text(encoding="utf-8").startswith(
        "from __future__ import annotations"
    )
    assert (
        root / "src" / "laser_garden" / "scenes" / "pause.py"
    ).read_text(encoding="utf-8").startswith(
        "from __future__ import annotations"
    )


def test_game_scaffold_command_ignores_global_cli_kwargs(
    tmp_path: Path,
) -> None:
    command = ScaffoldGameCommand()

    assert (
        command.execute(
            game_id="ball-vs-ball",
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
    (tmp_path / "games").mkdir()
    monkeypatch.chdir(tmp_path)

    processor = GameScaffoldProcessor(game_id="laser-garden")

    assert processor.run() == 0
    assert (tmp_path / "games" / "laser-garden" / "manage.py").exists()


def test_game_scaffold_dry_run_does_not_write_files(
    tmp_path: Path,
    capsys,
) -> None:
    processor = GameScaffoldProcessor(
        game_id="laser-garden",
        destination=str(tmp_path),
        dry_run=True,
    )

    assert processor.run() == 0
    assert not (tmp_path / "laser-garden").exists()
    assert "laser-garden" in capsys.readouterr().out


def test_system_lab_lists_and_runs_registered_case(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    SystemLabRegistry.clear()
    package_dir = tmp_path / "labcases"
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "sample_cases.py").write_text(
        '''from mini_arcade.modules.system_lab.registry import BaseSystemLabCase, SystemLabRegistry


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
''',
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    assert SystemLabProcessor(module=["labcases.sample_cases"], list=True).run() == 0
    assert "counter_case" in capsys.readouterr().out

    assert (
        SystemLabProcessor(
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


def test_system_lab_command_ignores_global_cli_kwargs(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    SystemLabRegistry.clear()
    package_dir = tmp_path / "labcases"
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "sample_cases.py").write_text(
        '''from mini_arcade.modules.system_lab.registry import BaseSystemLabCase, SystemLabRegistry


class CounterSystem:
    def step(self, ctx):
        ctx["value"] += 1


@SystemLabRegistry.implementation("counter_case")
class CounterCase(BaseSystemLabCase):
    def build_system(self):
        return CounterSystem()

    def build_context(self):
        return {"value": 0}
''',
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    command = SystemLabCommand()
    assert (
        command.execute(
            module=["labcases.sample_cases"],
            list=True,
            verbose=2,
        )
        == 0
    )
    assert "counter_case" in capsys.readouterr().out


def test_system_lab_cli_parses_module_without_swallowing_flags() -> None:
    cli = _build_cli()

    args = cli.parse_args(
        [
            "system-lab",
            "--module",
            "experiments.procedural_fire_lab.system_lab_case",
            "--list",
            "--json",
        ]
    )

    assert args.module == ["experiments.procedural_fire_lab.system_lab_case"]
    assert args.list is True
    assert args.json is True


def test_system_lab_visual_runner_path(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    SystemLabRegistry.clear()
    package_dir = tmp_path / "labcases_visual"
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "sample_cases.py").write_text(
        '''from mini_arcade.modules.system_lab.registry import BaseSystemLabCase, SystemLabRegistry


@SystemLabRegistry.implementation("visual_case")
class VisualCase(BaseSystemLabCase):
    def build_system(self):
        raise RuntimeError("headless path should not be used")

    def build_context(self):
        raise RuntimeError("headless path should not be used")

    def run_visual(self):
        print("visual runner launched")
        return 0
''',
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    assert (
        SystemLabProcessor(
            module=["labcases_visual.sample_cases"],
            case="visual_case",
            visual=True,
        ).run()
        == 0
    )
    assert "visual runner launched" in capsys.readouterr().out


def test_system_lab_visual_runner_auto_selects_single_case(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    SystemLabRegistry.clear()
    package_dir = tmp_path / "labcases_visual_auto"
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "sample_cases.py").write_text(
        '''from mini_arcade.modules.system_lab.registry import BaseSystemLabCase, SystemLabRegistry


@SystemLabRegistry.implementation("visual_case")
class VisualCase(BaseSystemLabCase):
    def build_system(self):
        raise RuntimeError("headless path should not be used")

    def build_context(self):
        raise RuntimeError("headless path should not be used")

    def run_visual(self):
        print("visual auto runner launched")
        return 0
''',
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    assert (
        SystemLabProcessor(
            module=["labcases_visual_auto.sample_cases"],
            visual=True,
        ).run()
        == 0
    )
    assert "visual auto runner launched" in capsys.readouterr().out


def test_load_command_packages_skips_non_command_modules(
    tmp_path: Path,
    monkeypatch,
) -> None:
    root = tmp_path / "demo_pkg"
    modules_dir = root / "modules"
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
        '''from mini_arcade.cli.base_command import BaseCommand
from mini_arcade.cli.registry import CommandRegistry


@CommandRegistry.implementation("temp-light-cmd")
class TempLightCommand(BaseCommand):
    name = "temp-light-cmd"

    def _execute(self, **kwargs):
        return 0
''',
        encoding="utf-8",
    )

    monkeypatch.syspath_prepend(str(tmp_path))
    loaded = load_command_packages(
        base_namespace="demo_pkg.modules",
        base_dir=modules_dir,
    )

    assert [pkg.import_name for pkg in loaded] == ["demo_pkg.modules.light_cmd"]
    assert CommandRegistry.contains("temp-light-cmd")
