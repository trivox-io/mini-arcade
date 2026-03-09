# scene/menu_scene_base

## Goal

Build a production-style menu using `BaseMenuScene` with:

- menu navigation (`UP`, `DOWN`, `ENTER`)
- command-driven actions
- dynamic menu labels (`label_fn`)
- scene transition from menu -> preview -> menu

## Why this tutorial exists

`BaseMenuScene` is the menu foundation used in shipped games
(`deja-bounce`, `asteroids`, `space-invaders`). This tutorial isolates that
pattern in a small example before pause overlays and complex gameplay scenes.

## Source map

- Settings profile:
  `examples/settings/scene/menu_scene_base.yml`
- Example builder:
  `examples/catalog/scene/menu_scene_base/main.py`
- Menu scene:
  `examples/catalog/scene/menu_scene_base/scenes/menu.py`
- Commands:
  `examples/catalog/scene/menu_scene_base/scenes/commands.py`
- Preview scene:
  `examples/catalog/scene/menu_scene_base/scenes/preview.py`
- Core menu base:
  `packages/mini-arcade-core/src/mini_arcade_core/ui/menu.py`

## What `BaseMenuScene` gives you

When your scene extends `BaseMenuScene`, the base class wires:

- `MenuInputSystem`:
  `InputFrame -> MenuIntent` (`UP`, `DOWN`, `ENTER`/`SPACE`, `ESC`)
- `MenuNavigationSystem`:
  selection movement + cooldown behavior
- `MenuActionSystem`:
  executes selected `MenuItem.command_factory()`
- `MenuRenderSystem`:
  renders menu through queued UI draw op

You only implement:

- `menu_title` property
- `menu_style()` returning `MenuStyle`
- `menu_items()` returning `list[MenuItem]`
- optional `quit_command()` override for `ESC`

## Example architecture

This tutorial uses two scenes:

1. `menu_scene_base_menu`:
   `BaseMenuScene` subclass with three items.
2. `menu_scene_base_preview`:
   simple `SimScene` that shows selected difficulty and returns to menu on `ESC`.

Menu items:

- `START PREVIEW` -> `StartPreviewCommand` (`ChangeSceneCommand`)
- `DIFFICULTY: <LEVEL>` -> `CycleDifficultyCommand`
- `QUIT` -> `QuitCommand`

## Dynamic label pattern (`label_fn`)

`MenuItem` supports label recomputation each frame:

```python
MenuItem(
    "difficulty",
    "DIFFICULTY",
    CycleDifficultyCommand,
    label_fn=self._difficulty_label,
)
```

The callback reads runtime settings:

```python
@staticmethod
def _difficulty_label(ctx: RuntimeContext) -> str:
    level = str(ctx.settings.difficulty.level).upper()
    return f"DIFFICULTY: {level}"
```

`CycleDifficultyCommand` mutates `context.settings.difficulty.level`, and the
next tick redraws the new label automatically.

## Config requirements

This tutorial profile includes:

- `scene.initial_scene: menu_scene_base_menu`
- scene discovery package for this example
- `mini_arcade_core.scenes` for built-in overlay (`F1`)

```yaml
scene:
  initial_scene: menu_scene_base_menu
  scene_registry:
    discover_packages:
      - examples.catalog.scene.menu_scene_base
      - mini_arcade_core.scenes
```

## Run

Default:

```bash
mini-arcade run --example scene/menu_scene_base
```

Force pygame:

```bash
mini-arcade run --example scene/menu_scene_base --pass-through --backend pygame
```

Force native:

```bash
mini-arcade run --example scene/menu_scene_base --pass-through --backend native
```

## What to verify

1. `UP`/`DOWN` changes selected menu item.
2. `ENTER` on `START PREVIEW` moves to preview scene.
3. `ESC` in preview returns to menu.
4. selecting `DIFFICULTY` cycles the value (`EASY/NORMAL/HARD/INSANE`).
5. difficulty value persists into preview scene text.
6. `F1` toggles built-in debug overlay in both scenes.

## How this maps to real games

Real game menu scenes follow the same base contract:

- `games/deja-bounce/src/deja_bounce/scenes/menu.py`
- `games/asteroids/src/asteroids/scenes/menu.py`
- `games/space-invaders/src/space_invaders/scenes/menu.py`

Pause menus in those games also extend `BaseMenuScene`, but with overlay style
and different quit behavior.

## Related concepts

- Menu internals:
  [../../concepts/menu_scenes.md](../../concepts/menu_scenes.md)
- Scene stack internals:
  [../../concepts/scenes_internals.md](../../concepts/scenes_internals.md)
- Scene transitions internals:
  [../../concepts/scene_transitions.md](../../concepts/scene_transitions.md)
- Configuration internals:
  [../../concepts/configuration.md](../../concepts/configuration.md)

## Next step

- Deep-dive transition behavior:
  [change_scene.md](change_scene.md)
