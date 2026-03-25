"""
Processor for creating starter Mini Arcade game projects.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from mini_arcade.cli.base_command_processor import BaseCommandProcessor
from mini_arcade.cli.exceptions import CommandException
from mini_arcade.common.game_paths import (
    CLONE_GAMES_DIRNAME,
    DEFAULT_GAME_SCAFFOLD_DESTINATION,
)
from mini_arcade.constants import APP


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
            "game-id must be kebab-case using letters, numbers, and hyphens"
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
class ScaffoldSpec:
    """
    Specification for generating a game scaffold, containing all necessary information
    about the game and project structure.

    :ivar game_id: The unique identifier for the game, used for package naming and
        project structure.
    :ivar package: The Python package name for the game's source code.
    :ivar title: The human-readable title for the game.
    :ivar target_dir: The target directory where the game scaffold will be created.
    :ivar dependency_series: The version series (e.g. "0.1") of
        mini-arcade dependencies to use in the generated pyproject.toml.
    """

    game_id: str
    package: str
    title: str
    target_dir: Path
    dependency_series: str


def _template_files(spec: ScaffoldSpec) -> dict[Path, str]:
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
        / "manage.py": f"""from {package}.app import run

if __name__ == "__main__":
    run()
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


@dataclass(init=False)
class GameScaffoldProcessor(BaseCommandProcessor):
    """
    Processor for creating starter Mini Arcade game projects.

    :ivar game_id (str): The unique identifier for the game, used for package naming and
        project structure.
    :ivar package (str | None): Optional custom package name for the game's source code.
    :ivar title (str | None): Optional human-readable title for the game.
    :ivar destination (str): The parent directory where the game scaffold will be created.
    :ivar force (bool): Whether to overwrite existing files if the target directory already exists
        (default is False).
    :ivar dry_run (bool): If True, do not create any files but print the intended
        actions (default is False).
    :ivar clone (bool): If True, default destination becomes ``games/`` instead
        of ``originals/``.
    """

    game_id: str
    package: str | None = None
    title: str | None = None
    destination: str = DEFAULT_GAME_SCAFFOLD_DESTINATION
    clone: bool = False
    force: bool = False
    dry_run: bool = False

    def __init__(self, **kwargs):
        self.game_id = kwargs.get("game_id")
        self.package = kwargs.get("package")
        self.title = kwargs.get("title")
        self.clone = bool(kwargs.get("clone", False))
        destination = kwargs.get("destination")
        self.destination = destination or (
            CLONE_GAMES_DIRNAME
            if self.clone
            else DEFAULT_GAME_SCAFFOLD_DESTINATION
        )
        self.force = bool(kwargs.get("force", False))
        self.dry_run = bool(kwargs.get("dry_run", False))

    def _build_spec(self) -> ScaffoldSpec:
        game_id = _validate_game_id(self.game_id)
        package = _validate_package_name(
            self.package or _default_package_name(game_id)
        )
        title = (self.title or _default_title(game_id)).strip()
        target_dir = Path(self.destination).expanduser().resolve() / game_id
        dep = _dependency_series(APP.version)
        return ScaffoldSpec(
            game_id=game_id,
            package=package,
            title=title,
            target_dir=target_dir,
            dependency_series=dep,
        )

    def _write_files(self, files: dict[Path, str], *, force: bool) -> None:
        for path, content in files.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists() and not force:
                raise CommandException(
                    f"Refusing to overwrite existing file: {path}"
                )
            path.write_text(content, encoding="utf-8")

    def run(self) -> int:
        spec = self._build_spec()
        files = _template_files(spec)

        if spec.target_dir.exists() and not self.force and not self.dry_run:
            raise CommandException(
                f"Target directory already exists: {spec.target_dir}"
            )

        if self.dry_run:
            print(f"Scaffold target: {spec.target_dir}")
            for path in sorted(files):
                print(path.relative_to(spec.target_dir.parent))
            return 0

        spec.target_dir.mkdir(parents=True, exist_ok=True)
        self._write_files(files, force=self.force)
        print(f"Created game scaffold at {spec.target_dir}")
        return 0
