"""
Game scaffold implementation owned by the game command domain.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from mini_arcade.cli.exceptions import CommandException
from mini_arcade.commands.shared.scaffold import (
    BaseScaffoldProcessor,
    BaseScaffoldSpec,
)
from mini_arcade.common.game_paths import GAMES_DIRNAME
from mini_arcade.constants import APP

from .models import ScaffoldKwargs


def _dependency_series(version: str) -> str:
    parts = version.split(".")
    if len(parts) < 2:
        return version
    return f"{parts[0]}.{parts[1]}"


def _default_package_name(game_id: str) -> str:
    return game_id.strip().lower().replace("-", "_")


def _default_title(game_id: str) -> str:
    return game_id.replace("-", " ").replace("_", " ").title()


def _validate_game_id(game_id: str) -> str:
    normalized = game_id.strip().lower()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", normalized):
        raise CommandException(
            "id must be kebab-case using letters, numbers, and hyphens"
        )
    return normalized


def _validate_package_name(package: str) -> str:
    normalized = package.strip().lower()
    if not re.fullmatch(r"[a-z_][a-z0-9_]*", normalized):
        raise CommandException(
            "package must be snake_case and start with a letter or underscore"
        )
    return normalized


@dataclass(frozen=True)
class GameScaffoldSpec(BaseScaffoldSpec):
    """
    Specification for generating a Mini Arcade game scaffold.
    """

    game_id: str
    package: str
    title: str
    dependency_series: str


class GameScaffoldTemplateBuilder:
    """
    Builds the generated file set for a game scaffold.
    """

    def build(self, spec: GameScaffoldSpec) -> dict[Path, str]:
        game_id = spec.game_id
        package = spec.package
        title = spec.title
        dep = spec.dependency_series
        project_dir = spec.target_dir
        src_dir = project_dir / "src" / package
        play_dir = src_dir / "scenes" / "play"
        systems_dir = play_dir / "systems"

        return {
            project_dir
            / "pyproject.toml": f"""[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"

[project]
name = "{game_id}"
version = "0.1.0"
description = "{title} built with Mini Arcade."
requires-python = ">=3.9,<3.12"
dependencies = [
  "mini-arcade-core~={dep}",
  "mini-arcade~={dep}",
  "mini-arcade-pygame-backend~={dep}",
  "mini-arcade-native-backend~={dep}",
]

[tool.poetry]
packages = [{{ include = "{package}", from = "src" }}]

[project.scripts]
{game_id} = "{package}.app:run"

[tool.mini-arcade.game]
id = "{game_id}"
entrypoint = "manage.py"
source_roots = ["src"]
""",
            project_dir
            / "manage.py": f"""from __future__ import annotations

from pathlib import Path
import sys


def _find_repo_root(start: Path) -> Path | None:
    for candidate in (start, *start.parents):
        marker = candidate / "packages" / "mini-arcade" / "src"
        if marker.exists():
            return candidate
    return None


def _bootstrap_paths() -> None:
    project_root = Path(__file__).resolve().parent
    repo_root = _find_repo_root(project_root)
    paths = [project_root, project_root / "src"]

    if repo_root is not None:
        paths.extend(
            [
                repo_root,
                repo_root / "packages" / "mini-arcade" / "src",
                repo_root / "packages" / "mini-arcade-core" / "src",
                repo_root / "packages" / "mini-arcade-pygame-backend" / "src",
                repo_root / "packages" / "mini-arcade-native-backend" / "src",
            ]
        )

    for path in reversed(paths):
        value = str(path)
        if value not in sys.path:
            sys.path.insert(0, value)


_bootstrap_paths()

from mini_arcade.project_launcher import run_project_entrypoint


def _run_local() -> None:
    from {package}.app import run

    run()

if __name__ == "__main__":
    raise SystemExit(run_project_entrypoint(_run_local))
""",
            project_dir
            / "settings"
            / "settings.yml": f"""game:
  id: {game_id}

project:
  root: ${{settings_dir}}/..
  assets_root: ${{project_root}}/assets

scene:
  initial_scene: menu
  scene_registry:
    discover_packages:
      - {package}.scenes
      - mini_arcade_core.scenes

engine_config:
  fps: 60
  virtual_resolution: [960, 540]
  enable_profiler: false

backend:
  provider: pygame
  window:
    width: 960
    height: 540
    title: {title}
    resizable: true
  renderer:
    background_color: [18, 18, 24]
  audio:
    enable: false

gameplay:
  difficulty:
    default: normal
""",
            src_dir / "__init__.py": "",
            src_dir
            / "__main__.py": f"""from {package}.app import run

if __name__ == "__main__":
    run()
""",
            src_dir
            / "app.py": f"""from __future__ import annotations

from mini_arcade.common.backend_loader import BackendLoader
from mini_arcade.common.settings import Settings
from mini_arcade_core import run_game


def run() -> None:
    settings = Settings.for_game("{game_id}", required=True)

    backend_cfg = settings.backend_defaults(resolve_paths=True)
    backend = BackendLoader.load_backend(backend_cfg)

    engine_cfg = settings.engine_config_defaults()
    scene_cfg = settings.scene_defaults()
    gameplay_cfg = settings.gameplay_defaults()

    run_game(
        engine_config=engine_cfg,
        scene_config=scene_cfg,
        backend=backend,
        gameplay_config=gameplay_cfg,
    )


if __name__ == "__main__":
    run()
""",
            src_dir
            / "scenes"
            / "__init__.py": """from . import menu, pause
from .play import scene
""",
            src_dir
            / "scenes"
            / "commands.py": """from mini_arcade_core.engine.commands import (
    Command,
    CommandContext,
    PushSceneIfMissingCommand,
    RemoveSceneCommand,
)
from mini_arcade_core.engine.scenes.models import ScenePolicy


class StartGameCommand(Command):
    def execute(self, context: CommandContext):
        context.managers.scenes.change("play")


class PauseGameCommand(Command):
    def execute(self, context: CommandContext):
        PushSceneIfMissingCommand(
            "pause",
            as_overlay=True,
            policy=ScenePolicy(
                blocks_update=True,
                blocks_input=True,
                is_opaque=False,
                receives_input=True,
            ),
        ).execute(context)


class ContinueCommand(Command):
    def execute(self, context: CommandContext):
        RemoveSceneCommand("pause").execute(context)


class BackToMenuCommand(Command):
    def execute(self, context: CommandContext):
        context.managers.scenes.change("menu")
""",
            src_dir
            / "scenes"
            / "menu.py": f"""from __future__ import annotations

from mini_arcade_core.engine.commands import QuitCommand
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.ui.menu import BaseMenuScene, MenuItem

from {package}.scenes.commands import StartGameCommand


@register_scene("menu")
class MenuScene(BaseMenuScene):
    @property
    def menu_title(self) -> str | None:
        return "{title.upper()}"

    def menu_items(self):
        return [
            MenuItem("start", "START", StartGameCommand),
            MenuItem("quit", "QUIT", QuitCommand),
        ]
""",
            src_dir
            / "scenes"
            / "pause.py": f"""from __future__ import annotations

from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.ui.menu import BaseMenuScene, MenuItem

from {package}.scenes.commands import BackToMenuCommand, ContinueCommand


@register_scene("pause")
class PauseScene(BaseMenuScene):
    @property
    def menu_title(self) -> str | None:
        return "PAUSED"

    def menu_items(self):
        return [
            MenuItem("continue", "CONTINUE", ContinueCommand),
            MenuItem("menu", "MAIN MENU", BackToMenuCommand),
        ]

    def quit_command(self):
        return ContinueCommand()
""",
            play_dir / "__init__.py": "",
            play_dir
            / "models.py": """from dataclasses import dataclass

from mini_arcade_core.scenes.sim_scene import BaseIntent, BaseTickContext, BaseWorld


@dataclass
class PlayWorld(BaseWorld):
    viewport: tuple[float, float]
    player_x: float = 100.0
    player_speed: float = 260.0


@dataclass(frozen=True)
class PlayIntent(BaseIntent):
    move_x: float = 0.0
    pause: bool = False


@dataclass
class PlayTickContext(BaseTickContext[PlayWorld, PlayIntent]):
    pass
""",
            play_dir
            / "bootstrap.py": """from __future__ import annotations

from .models import PlayWorld


def build_play_world(*, viewport: tuple[float, float]) -> PlayWorld:
    vw, _ = viewport
    return PlayWorld(
        entities=[],
        viewport=viewport,
        player_x=vw * 0.5,
    )
""",
            play_dir
            / "pipeline.py": """from __future__ import annotations

from .systems import PlayRenderSystem, PlayRulesSystem


def build_play_systems() -> tuple[object, ...]:
    return (
        PlayRulesSystem(),
        PlayRenderSystem(),
    )
""",
            play_dir
            / "scene.py": f"""from __future__ import annotations

from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.bootstrap import scene_viewport
from mini_arcade_core.scenes.game_scene import GameScene, GameSceneSystemsConfig

from {package}.scenes.commands import PauseGameCommand
from {package}.scenes.play.bootstrap import build_play_world
from {package}.scenes.play.models import PlayIntent, PlayTickContext, PlayWorld
from {package}.scenes.play.pipeline import build_play_systems


def _build_play_intent(actions, _ctx: PlayTickContext) -> PlayIntent:
    return PlayIntent(
        move_x=actions.value("move_x"),
        pause=actions.pressed("pause"),
    )


@register_scene("play")
class PlayScene(GameScene[PlayTickContext, PlayWorld]):
    tick_context_type = PlayTickContext
    systems_config = GameSceneSystemsConfig(
        controls_scene_key="play",
        intent_factory=_build_play_intent,
        input_fallback_bindings={{
            "move_x": {{
                "type": "axis",
                "negative_keys": ["LEFT", "A"],
                "positive_keys": ["RIGHT", "D"],
            }},
            "pause": {{
                "type": "digital",
                "keys": ["ESCAPE"],
            }},
        }},
        pause_command_factory=lambda _ctx: PauseGameCommand(),
    )

    def on_enter(self):
        self.world = build_play_world(viewport=scene_viewport(self))
        self.systems.extend(build_play_systems())
""",
            systems_dir
            / "__init__.py": """from .render import PlayRenderSystem
from .rules import PlayRulesSystem

__all__ = [
    "PlayRenderSystem",
    "PlayRulesSystem",
]
""",
            systems_dir
            / "rules.py": """from dataclasses import dataclass

from mini_arcade_core.scenes.systems.base_system import BaseSystem
from mini_arcade_core.scenes.systems.phases import SystemPhase

from ..models import PlayTickContext


@dataclass
class PlayRulesSystem(BaseSystem[PlayTickContext]):
    name: str = "play_rules"
    phase: int = SystemPhase.SIMULATION
    order: int = 20

    def step(self, ctx: PlayTickContext):
        if ctx.intent is None:
            return

        world = ctx.world
        world.player_x += ctx.intent.move_x * world.player_speed * ctx.dt
        world.player_x = max(20.0, min(world.viewport[0] - 20.0, world.player_x))
""",
            systems_dir
            / "render.py": """from dataclasses import dataclass

from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.scenes.systems.base_system import BaseSystem
from mini_arcade_core.scenes.systems.phases import SystemPhase

from ..models import PlayTickContext


@dataclass
class PlayRenderSystem(BaseSystem[PlayTickContext]):
    name: str = "play_render"
    phase: int = SystemPhase.RENDERING
    order: int = 100

    def step(self, ctx: PlayTickContext):
        world = ctx.world
        vw, vh = world.viewport

        def draw(backend):
            backend.render.draw_rect(0, 0, int(vw), int(vh), color=(12, 14, 20))
            backend.render.draw_rect(
                int(world.player_x) - 20,
                int(vh) - 60,
                40,
                20,
                color=(240, 240, 240),
            )
            backend.text.draw(
                16,
                16,
                "Arrows or A/D to move | Esc pause",
                color=(220, 220, 220),
                font_size=18,
            )

        ctx.packet = RenderPacket.from_ops([draw])
""",
            src_dir / "entities" / "__init__.py": "",
            src_dir / "controllers" / "__init__.py": "",
            project_dir / "assets" / "sprites" / ".gitkeep": "",
            project_dir / "assets" / "fonts" / ".gitkeep": "",
            project_dir / "assets" / "sfx" / ".gitkeep": "",
        }


class GameScaffoldProcessor(BaseScaffoldProcessor[GameScaffoldSpec]):
    """
    Processor for creating starter Mini Arcade game projects.
    """

    def __init__(self, **kwargs):
        self.kwargs = ScaffoldKwargs.from_dict(kwargs)
        self.force = bool(self.kwargs.force)
        self.dry_run = bool(self.kwargs.dry_run)
        self._template_builder = GameScaffoldTemplateBuilder()

    def _build_spec(self) -> GameScaffoldSpec:
        game_id = _validate_game_id(self.kwargs.id)
        package = _validate_package_name(
            self.kwargs.package or _default_package_name(game_id)
        )
        title = (self.kwargs.title or _default_title(game_id)).strip()
        target_dir = (
            Path(self.kwargs.destination or GAMES_DIRNAME).expanduser().resolve()
            / game_id
        )
        dependency_series = _dependency_series(APP.version)
        return GameScaffoldSpec(
            game_id=game_id,
            package=package,
            title=title,
            target_dir=target_dir,
            dependency_series=dependency_series,
        )

    def _template_files(self, spec: GameScaffoldSpec) -> dict[Path, str]:
        return self._template_builder.build(spec)

    def _created_message(self, spec: GameScaffoldSpec) -> str:
        return f"Created game scaffold at {spec.target_dir}"


__all__ = [
    "GameScaffoldProcessor",
    "GameScaffoldSpec",
]
