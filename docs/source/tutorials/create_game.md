# Create a Game

## Goal

Build a new CLI-runnable game that works with:

- `mini-arcade run --game <game-id>`
- `python manage.py` from the game folder

This guide documents the current pattern used by the reference games in this repository.

## Prerequisites

- Working dev environment (see [../contributing/dev_setup.md](../contributing/dev_setup.md))
- Repo checkout with editable installs
- Basic Python familiarity

## Naming Rules

Choose these values first:

- `game-id`: CLI id and folder id (kebab-case), for example `my-first-game`
- `python_package`: import package (snake_case), for example `my_first_game`

Recommended mapping:

- folder: `games/my-first-game/`
- package: `games/my-first-game/src/my_first_game/`
- settings profile load call: `Settings.for_game("my-first-game", required=True)`

## Required Layout

Use this minimum structure:

```text
games/my-first-game/
  pyproject.toml
  manage.py
  settings/
    settings.yml
  src/my_first_game/
    __init__.py
    __main__.py
    app.py
    scenes/
      __init__.py
      commands.py
      menu.py
      pause.py
      play/
        __init__.py
        scene.py
        models.py
        systems/
          __init__.py
          input.py
          rules.py
          render.py
```

## Step 1: `pyproject.toml`

Minimal template:

```toml
[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"

[project]
name = "my-first-game"
version = "0.1.0"
description = "My first mini-arcade game."
requires-python = ">=3.9,<3.12"
dependencies = [
  "mini-arcade-core~=1.1",
  "mini-arcade~=1.1",
  "mini-arcade-pygame-backend~=1.0",
  "mini-arcade-native-backend~=1.0",
]

[tool.poetry]
packages = [{ include = "my_first_game", from = "src" }]

[project.scripts]
my-first-game = "my_first_game.app:run"

[tool.mini-arcade.game]
id = "my-first-game"
entrypoint = "manage.py"
source_roots = ["src"]
```

`[tool.mini-arcade.game]` is required for CLI game discovery.

## Step 2: Launchers (`manage.py`, `__main__.py`)

`manage.py`:

```python
from my_first_game.app import run

if __name__ == "__main__":
    run()
```

`src/my_first_game/__main__.py`:

```python
from my_first_game.app import run

if __name__ == "__main__":
    run()
```

## Step 3: Settings-Driven App Bootstrap (`app.py`)

Use this exact startup flow:

```python
from __future__ import annotations

from mini_arcade.modules.backend_loader import BackendLoader
from mini_arcade.modules.settings import Settings
from mini_arcade_core import run_game


def run() -> None:
    settings = Settings.for_game("my-first-game", required=True)

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
```

Why this matters:

- keeps bootstrap consistent across games
- allows backend/fps/scene defaults in YAML
- avoids hardcoding backend classes in game code

## Step 4: Game Settings (`settings/settings.yml`)

Use this baseline:

```yaml
game:
  id: my-first-game

project:
  root: ${settings_dir}/..
  assets_root: ${project_root}/assets

scene:
  initial_scene: menu
  scene_registry:
    discover_packages:
      - my_first_game.scenes
      - mini_arcade_core.scenes

engine_config:
  fps: 60
  virtual_resolution: [960, 540]
  enable_profiler: false
  postfx:
    enabled: false
    active: []

backend:
  provider: pygame
  window:
    width: 960
    height: 540
    title: My First Game
    resizable: true
  renderer:
    background_color: [18, 18, 24]
  audio:
    enable: false

gameplay:
  difficulty:
    default: normal
```

## Step 5: Scene Commands (`scenes/commands.py`)

```python
from mini_arcade_core.engine.commands import (
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
```

## Step 6: Menu and Pause Scenes

`scenes/menu.py`:

```python
from mini_arcade_core.engine.commands import QuitCommand
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.ui.menu import BaseMenuScene, MenuItem

from my_first_game.scenes.commands import StartGameCommand


@register_scene("menu")
class MenuScene(BaseMenuScene):
    @property
    def menu_title(self) -> str | None:
        return "MY FIRST GAME"

    def menu_items(self):
        return [
            MenuItem("start", "START", StartGameCommand),
            MenuItem("quit", "QUIT", QuitCommand),
        ]
```

`scenes/pause.py`:

```python
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.ui.menu import BaseMenuScene, MenuItem

from my_first_game.scenes.commands import BackToMenuCommand, ContinueCommand


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
```

## Step 7: Gameplay Scene with Systems

`scenes/play/models.py`:

```python
from dataclasses import dataclass

from mini_arcade_core.scenes.sim_scene import BaseIntent, BaseTickContext, BaseWorld


@dataclass
class PlayWorld(BaseWorld):
    viewport: tuple[float, float]
    player_x: float = 100.0
    player_speed: float = 260.0


@dataclass(frozen=True)
class PlayIntent(BaseIntent):
    move_x: float
    pause: bool = False


@dataclass
class PlayTickContext(BaseTickContext[PlayWorld, PlayIntent]):
    pass
```

`scenes/play/systems/input.py`:

```python
from mini_arcade_core.backend.keys import Key
from mini_arcade_core.scenes.systems.builtins import (
    ActionIntentSystem,
    ActionMap,
    AxisActionBinding,
    DigitalActionBinding,
)

from my_first_game.scenes.play.models import PlayIntent, PlayTickContext

PLAY_ACTIONS = ActionMap(
    bindings={
        "move_x": AxisActionBinding(
            negative_keys=(Key.LEFT, Key.A),
            positive_keys=(Key.RIGHT, Key.D),
        ),
        "pause": DigitalActionBinding(keys=(Key.ESCAPE,)),
    }
)


def _build_intent(actions, _ctx: PlayTickContext) -> PlayIntent:
    return PlayIntent(
        move_x=actions.value("move_x"),
        pause=actions.pressed("pause"),
    )


class PlayInputSystem(ActionIntentSystem[PlayTickContext, PlayIntent]):
    def __init__(self):
        super().__init__(
            action_map=PLAY_ACTIONS,
            intent_factory=_build_intent,
            name="play_input",
        )
```

`scenes/play/systems/rules.py`:

```python
from dataclasses import dataclass

from mini_arcade_core.scenes.systems.base_system import BaseSystem
from mini_arcade_core.scenes.systems.phases import SystemPhase

from my_first_game.scenes.commands import PauseGameCommand
from my_first_game.scenes.play.models import PlayTickContext


@dataclass
class PlayRulesSystem(BaseSystem[PlayTickContext]):
    name: str = "play_rules"
    phase: int = SystemPhase.SIMULATION
    order: int = 20

    def step(self, ctx: PlayTickContext):
        intent = ctx.intent
        if intent is None:
            return

        world = ctx.world
        world.player_x += intent.move_x * world.player_speed * ctx.dt
        world.player_x = max(20.0, min(world.viewport[0] - 20.0, world.player_x))

        if intent.pause:
            ctx.commands.push(PauseGameCommand())
```

`scenes/play/systems/render.py`:

```python
from dataclasses import dataclass

from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.scenes.systems.base_system import BaseSystem
from mini_arcade_core.scenes.systems.phases import SystemPhase

from my_first_game.scenes.play.models import PlayTickContext


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
                int(world.player_x) - 20, int(vh) - 60, 40, 20, color=(240, 240, 240)
            )
            backend.text.draw(16, 16, "ESC pause", color=(220, 220, 220), font_size=18)

        ctx.packet = RenderPacket.from_ops([draw])
```

`scenes/play/scene.py`:

```python
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.game_scene import GameScene

from my_first_game.scenes.play.models import PlayTickContext, PlayWorld
from my_first_game.scenes.play.systems.input import PlayInputSystem
from my_first_game.scenes.play.systems.render import PlayRenderSystem
from my_first_game.scenes.play.systems.rules import PlayRulesSystem


@register_scene("play")
class PlayScene(GameScene[PlayTickContext, PlayWorld]):
    tick_context_type = PlayTickContext

    def on_enter(self):
        vw, vh = self.context.services.window.get_virtual_size()
        self.world = PlayWorld(
            entities=[],
            viewport=(vw, vh),
            player_x=vw * 0.5,
        )
        self.systems.extend(
            [
                PlayInputSystem(),
                PlayRulesSystem(),
                PlayRenderSystem(),
            ]
        )
```

## Step 8: Ensure Scene Discovery Imports

`src/my_first_game/scenes/__init__.py` should import scene modules so decorators run:

```python
from . import menu, pause
from .play import scene
```

## Step 9: Run and Verify

From repo root:

```bash
mini-arcade run --game my-first-game
```

From game folder:

```bash
python manage.py
```

Expected result:

- menu scene opens
- ENTER starts `play`
- ESC from `play` opens pause overlay
- continue/menu actions work

## Common Failure Modes

- `Game '<id>' not found`: folder under `games/` does not match `--game`.
- `Missing [tool.mini-arcade.game]`: metadata block missing in `pyproject.toml`.
- `produced no RenderPacket`: render system did not assign `ctx.packet`.
- `scene id not found`: module with `@register_scene(...)` was not imported/discovered.
- font/audio path issues: use `${assets_root}` and `backend_defaults(resolve_paths=True)`.

## AI Agent Checklist

When generating a new game automatically, enforce this sequence:

1. Create folder/package layout exactly as documented.
2. Write `pyproject.toml` with `[tool.mini-arcade.game]`.
3. Add `manage.py`, `__main__.py`, and settings-driven `app.py`.
4. Create `settings/settings.yml` with `scene`, `engine_config`, and `backend`.
5. Create at least one registered gameplay scene plus one menu scene.
6. Ensure `scenes/__init__.py` imports modules containing `@register_scene`.
7. Run `mini-arcade run --game <id>` and fix import/config/runtime errors.

This gives a deterministic baseline that matches the current Mini Arcade runtime model.
