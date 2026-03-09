# Menu Scenes Internals

## Purpose

Explain how `BaseMenuScene` works internally, what extension points it exposes,
and how to apply it for main menus and pause overlays.

## Core implementation

Main file:

- `packages/mini-arcade-core/src/mini_arcade_core/ui/menu.py`

Key types:

- `MenuItem`:
  menu entry id, static label, `command_factory`, optional `label_fn`
- `MenuStyle`:
  style/layout options (background, panel, button style, hint, text colors)
- `Menu`:
  render + selection state + layout calculations
- `BaseMenuScene`:
  scene base class that wires menu systems

## BaseMenuScene contract

Implement in your scene subclass:

- `menu_title`:
  title text shown at top (`None` hides title)
- `menu_style()`:
  returns `MenuStyle` for look and layout
- `menu_items()`:
  returns menu entries and command factories

Optional:

- `quit_command()`:
  command used when `ESC` is pressed in menu
  (default is `QuitCommand`)

## Per-frame system pipeline

`BaseMenuScene.on_enter()` registers these systems in order:

1. `MenuInputSystem`
2. `MenuNavigationSystem`
3. `MenuActionSystem`
4. `MenuRenderSystem`

Runtime flow:

1. input keys become `MenuIntent`
2. selection index updates (with cooldown)
3. selected action enqueues command
4. menu is rendered as UI draw op

## Command model in menus

`MenuItem.command_factory` returns a command instance each selection.

Typical commands:

- `ChangeSceneCommand(...)` for scene transitions
- `RemoveSceneCommand(...)` for dismissing pause overlays
- `QuitCommand()` for full exit
- custom commands mutating gameplay settings (difficulty, toggles, etc.)

## Dynamic labels

`label_fn(ctx)` is evaluated each tick to resolve display label. This supports
menu text driven by runtime state:

- difficulty level
- audio on/off state
- control profile name
- backend/debug options

Pattern:

1. command mutates runtime state
2. next frame, `label_fn` reads updated state
3. menu label updates without scene restart

## Main menu vs pause overlay

Main menu pattern:

- usually opaque standalone scene
- sets `background_color`, `panel_color`, and button styles
- `ESC` often maps to `QuitCommand`

Pause overlay pattern:

- pushed with overlay `ScenePolicy` (`as_overlay=True`)
- menu style usually uses `overlay_color` dimming
- `quit_command()` typically resumes gameplay, not exit

See real game implementations:

- `games/deja-bounce/src/deja_bounce/scenes/menu.py`
- `games/deja-bounce/src/deja_bounce/scenes/pause.py`
- `games/asteroids/src/asteroids/scenes/menu.py`
- `games/asteroids/src/asteroids/scenes/pause.py`
- `games/space-invaders/src/space_invaders/scenes/menu.py`
- `games/space-invaders/src/space_invaders/scenes/pause.py`

## Common mistakes

- forgetting scene discovery package:
  menu scene never registers
- returning a command class that needs args without wrapping it in a factory
- mutating menu labels manually instead of using `label_fn`
- assuming pause overlay should use default `quit_command` (which exits game)

## Related tutorial

- `docs/source/tutorials/scene/menu_scene_base.md`

