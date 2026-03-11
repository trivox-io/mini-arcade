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
        draw_ops.py
        systems/
          __init__.py
          input.py
          rules.py
          render.py
    entities/
      __init__.py
      entity_id.py
      player.py
      enemy.py
    controllers/
      __init__.py
      cpu.py
  assets/
    sprites/
    fonts/
    sfx/
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

## Gameplay Architecture (Reference Model)

For non-trivial games, use this separation:

- `entities/`: reusable entity builders and IDs
- `scenes/<mode>/models.py`: world state, intent, tick context
- `scenes/<mode>/bootstrap.py`: world builders and asset/bootstrap helpers
- `scenes/<mode>/pipeline.py`: ordered system registration helpers
- `scenes/<mode>/spawn.py`: typed spawn specs and spawn policies when needed
- `scenes/<mode>/systems/*.py`: input, simulation rules, collisions, rendering
- `scenes/<mode>/draw_ops.py`: reusable `Drawable` overlays and specialized visuals
- `scenes/<mode>/scene.py`: scene registration and orchestration only

This is the same structure used in reference games:

- Deja Bounce:
  - `games/deja-bounce/src/deja_bounce/entities/`
  - `games/deja-bounce/src/deja_bounce/scenes/pong/models.py`
  - `games/deja-bounce/src/deja_bounce/scenes/pong/draw_ops.py`
  - `games/deja-bounce/src/deja_bounce/scenes/pong/systems/`
- Asteroids:
  - `games/asteroids/src/asteroids/entities/`
  - `games/asteroids/src/asteroids/scenes/asteroids/models.py`
  - `games/asteroids/src/asteroids/scenes/asteroids/draw_ops.py`
  - `games/asteroids/src/asteroids/scenes/asteroids/systems/`
- Space Invaders:
  - `games/space-invaders/src/space_invaders/entities/__init__.py`
  - `games/space-invaders/src/space_invaders/scenes/space_invaders/models.py`
  - `games/space-invaders/src/space_invaders/scenes/space_invaders/draw_ops.py`
  - `games/space-invaders/src/space_invaders/scenes/space_invaders/systems/`

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

`scenes/play/bootstrap.py`:

```python
from my_first_game.scenes.play.models import PlayWorld


def build_play_world(*, viewport: tuple[float, float]) -> PlayWorld:
    vw, vh = viewport
    return PlayWorld(
        entities=[],
        viewport=viewport,
        player_x=vw * 0.5,
    )
```

`scenes/play/pipeline.py`:

```python
from my_first_game.scenes.play.systems.render import PlayRenderSystem
from my_first_game.scenes.play.systems.rules import PlayRulesSystem


def build_play_systems():
    return (
        PlayRulesSystem(),
        PlayRenderSystem(),
    )
```

`scenes/play/scene.py`:

```python
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.bootstrap import scene_viewport
from mini_arcade_core.scenes.game_scene import GameScene, GameSceneSystemsConfig

from my_first_game.scenes.commands import PauseGameCommand
from my_first_game.scenes.play.bootstrap import build_play_world
from my_first_game.scenes.play.models import PlayTickContext, PlayWorld
from my_first_game.scenes.play.pipeline import build_play_systems


def _build_intent(actions, _ctx: PlayTickContext):
    ...


@register_scene("play")
class PlayScene(GameScene[PlayTickContext, PlayWorld]):
    tick_context_type = PlayTickContext
    systems_config = GameSceneSystemsConfig(
        controls_scene_key="play",
        intent_factory=_build_intent,
        pause_command_factory=lambda _ctx: PauseGameCommand(),
    )

    def on_enter(self):
        self.world = build_play_world(viewport=scene_viewport(self))
        self.systems.extend(build_play_systems())
```

## Entities Deep Dive (How to model game objects)

Reference pattern from all current games:

1. Define stable IDs (`entity_id.py`).
2. Create entity builder classes/functions in `entities/`.
3. Build entities with `BaseEntity.from_dict(...)`.
4. Store game-specific runtime flags as dynamic attributes when needed.

Typical base components in `from_dict`:

- `transform`: position, size, optional rotation
- `shape`: draw-time primitive shape metadata
- `collider`: collision shape metadata
- `kinematic`: velocity, acceleration, max speed
- `style`: primitive color/stroke style
- `sprite`: texture id for sprite-based rendering
- `anim`: animation metadata (frame list + fps)
- `life`: ttl/alive lifecycle metadata

Example entity builder (Asteroids-style):

```python
from mini_arcade_core.engine.entities import BaseEntity


class PlayerShip(BaseEntity):
    @staticmethod
    def build(x: float, y: float) -> "PlayerShip":
        ship: PlayerShip = PlayerShip.from_dict(
            {
                "id": 1,
                "name": "Ship",
                "transform": {
                    "center": {"x": x, "y": y},
                    "size": {"width": 24.0, "height": 28.0},
                    "rotation_deg": -90.0,
                },
                "shape": {"kind": "triangle"},
                "collider": {"kind": "circle", "radius": 12.0},
                "kinematic": {
                    "velocity": {"vx": 0.0, "vy": 0.0},
                    "acceleration": {"ax": 0.0, "ay": 0.0},
                    "max_speed": 330.0,
                },
                "style": {"fill": (240, 240, 245, 255)},
            }
        )
        ship.fire_cd = 0.0
        ship.invuln_timer = 0.0
        return ship
```

Practical guidance:

- Keep builder methods deterministic and free of side effects.
- Add `tags` for gameplay-facing categories you will query often.
- Declare `entity_id_domains` on `World` only when you need constrained runtime
  allocation or tracked cleanup.
- Keep scene-global state in `world`, not in entity classes.
- Use entity dynamic fields for per-entity runtime details only.

## World and Models Deep Dive

Use `models.py` to define:

- `World` (`BaseWorld`): all mutable scene state
- `Intent` (`BaseIntent`): normalized input snapshot per tick
- `TickContext` (`BaseTickContext`): typed pipeline context

Scale-up pattern from Space Invaders:

- Put timers/cooldowns in world (`ship_fire_timer`, `ufo_spawn_timer`)
- Put score/lives/round flags in world (`score`, `lives`, `game_over`)
- Put transient VFX state in world (`effects`, `fx_ttl`)
- Add helper selectors in world (`ship()`, `asteroids()`, `bullets()`)
- Prefer helper selectors backed by tags.
- Add `entity_id_domains` only for content that needs bounded spawn ids such as
  `bullet`, `missile`, or `asteroid`.

## DrawOps Deep Dive (Recommended for complex scenes)

For simple scenes, generating one `RenderPacket` with inline draw call is fine.

For medium/large scenes, use:

1. `draw_ops.py` classes that implement `Drawable[TContext]`
2. `ConfiguredQueuedRenderSystem` to compose default entity rendering, overlays,
   and targeted entity overrides
3. `RenderOverlay.from_drawable(...)` or `DrawCall(...)` wrappers for custom
   layered drawables

This is how Deja Bounce, Asteroids, and Space Invaders handle overlays/HUD/VFX.

Minimal `draw_ops.py` example:

```python
from mini_arcade_core.backend import Backend
from mini_arcade_core.scenes.sim_scene import Drawable

from my_first_game.scenes.play.models import PlayTickContext


class DrawHud(Drawable[PlayTickContext]):
    def draw(self, backend: Backend, ctx: PlayTickContext):
        backend.text.draw(
            12, 12, f"SCORE {ctx.world.score}", color=(255, 255, 255, 255)
        )
```

Minimal queued render system using draw ops:

```python
from dataclasses import dataclass

from mini_arcade_core.scenes.systems.builtins import (
    ConfiguredQueuedRenderSystem,
    RenderOverlay,
)
from mini_arcade_core.scenes.systems.phases import SystemPhase

from my_first_game.scenes.play.draw_ops import DrawHud
from my_first_game.scenes.play.models import PlayTickContext


@dataclass
class PlayRenderSystem(ConfiguredQueuedRenderSystem[PlayTickContext]):
    name: str = "play_render"
    phase: int = SystemPhase.RENDERING
    order: int = 100
    overlays = (
        RenderOverlay.from_drawable(DrawHud(), layer="ui", z=90),
    )
```

Layer guidance:

- `world`: entities and gameplay geometry
- `lighting`: glow/light overlays
- `ui`: HUD/menu text
- `effects`: transient FX/post-world overlays

## Systems Deep Dive (Pipeline design)

A robust system order for gameplay scenes:

1. Input systems (`SystemPhase.INPUT`)
2. Control systems (pause/hotkeys/commands) (`SystemPhase.CONTROL`)
3. Simulation systems (movement, collisions, rules) (`SystemPhase.SIMULATION`)
4. Rendering systems (`SystemPhase.RENDERING`)

Example from real games:

- Deja Bounce:
  - declarative gameplay shell -> intent commands -> movement bundles ->
    collision/rules -> render
- Asteroids:
  - declarative gameplay shell -> ship control -> motion bundle -> collision ->
    render
- Space Invaders:
  - declarative gameplay shell -> feature bundles + gameplay processors ->
    render

Rule of thumb:

- Systems mutate `ctx.world` and enqueue commands in `ctx.commands`.
- Exactly one render path must set `ctx.packet` each tick.
- Keep each system focused on one responsibility.
- Use `SystemBundle` when one feature is made from several reusable atomic
  processors.
- Keep long ordered system lists out of `scene.py`; prefer a local
  `pipeline.py` builder.

## GameScene shell

For most gameplay scenes, prefer `GameScene` plus `GameSceneSystemsConfig`
instead of hand-wiring input/pause/render every time.

Typical responsibilities:

- `controls_scene_key` + `intent_factory`: action bindings to typed intent
- `pause_command_factory`: built-in pause intent handling
- `intent_command_bindings`: one-shot command toggles
- `render_system_factory`: attach the scene render system

That keeps scene code focused on world bootstrap and custom gameplay systems.

In the reference games, that usually means:

- `scene.py` calls shared helpers such as `scene_viewport(...)` and
  `scene_entities_config(...)`
- `bootstrap.py` builds the initial world
- `pipeline.py` returns the ordered gameplay systems

## Asset and Texture Patterns

Use these patterns from reference games:

- Resolve asset root once (`find_assets_root()` helpers).
- Put larger asset/template loaders in `bootstrap.py`, not directly in
  `scene.py`.
- Cache texture lookups in scene methods (`self._tex(path)` pattern).
- Keep logical projectile/animation specs in `world` (not global module state).

This keeps startup predictable and avoids per-frame texture loading.

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

## Reference File Map (Use these as templates)

Deja Bounce (balanced baseline):

- `games/deja-bounce/src/deja_bounce/scenes/pong/scene.py`
- `games/deja-bounce/src/deja_bounce/scenes/pong/bootstrap.py`
- `games/deja-bounce/src/deja_bounce/scenes/pong/pipeline.py`
- `games/deja-bounce/src/deja_bounce/scenes/pong/models.py`
- `games/deja-bounce/src/deja_bounce/scenes/pong/draw_ops.py`
- `games/deja-bounce/src/deja_bounce/scenes/pong/systems/`
- `games/deja-bounce/src/deja_bounce/entities/`

Asteroids (shape-heavy rendering and bounded spawn domains):

- `games/asteroids/src/asteroids/scenes/asteroids/scene.py`
- `games/asteroids/src/asteroids/scenes/asteroids/bootstrap.py`
- `games/asteroids/src/asteroids/scenes/asteroids/pipeline.py`
- `games/asteroids/src/asteroids/scenes/asteroids/spawn.py`
- `games/asteroids/src/asteroids/scenes/asteroids/models.py`
- `games/asteroids/src/asteroids/scenes/asteroids/draw_ops.py`
- `games/asteroids/src/asteroids/scenes/asteroids/systems/render.py`
- `games/asteroids/src/asteroids/entities/`

Space Invaders (large scene decomposition and advanced overlays):

- `games/space-invaders/src/space_invaders/scenes/space_invaders/scene.py`
- `games/space-invaders/src/space_invaders/scenes/space_invaders/models.py`
- `games/space-invaders/src/space_invaders/scenes/space_invaders/draw_ops.py`
- `games/space-invaders/src/space_invaders/scenes/space_invaders/systems/render.py`
- `games/space-invaders/src/space_invaders/entities/__init__.py`
