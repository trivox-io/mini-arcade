# scene/minimal_scene

## Goal

Create the smallest useful `SimScene` example that:

- registers a scene id
- runs with both backends
- renders text and one animated primitive each frame

## What this tutorial demonstrates

This example connects:

1. Settings profile:
   `examples/settings/scene/minimal_scene.yml`
2. Example builder:
   `examples/catalog/scene/minimal_scene/main.py`
3. Runtime scene:
   `examples/catalog/scene/minimal_scene/scenes/scene.py`
4. Shared runner:
   `examples/_shared/runner.py`

Execution flow:

1. `build_example()` loads defaults from the settings profile.
2. Optional CLI overrides adjust backend/fps/window/virtual resolution.
3. Runner builds `EngineConfig` + `SceneConfig`.
4. Scene `minimal_scene` renders one debug panel and an animated rectangle.

## Run

Default:

```bash
mini-arcade run --example scene/minimal_scene
```

Force pygame:

```bash
mini-arcade run --example scene/minimal_scene --pass-through --backend pygame
```

Force native:

```bash
mini-arcade run --example scene/minimal_scene --pass-through --backend native
```

Override timing/resolution:

```bash
mini-arcade run --example scene/minimal_scene --pass-through --fps 72 --virtual-width 960 --virtual-height 540
```

## Scene anatomy

`scenes/scene.py` does four things:

1. Defines `SCENE_ID = "minimal_scene"`.
2. Registers the class with `@register_scene(SCENE_ID)`.
3. Overrides `tick(input_frame, dt)` and tracks frame/time.
4. Returns a `RenderPacket` with one draw callable.

The draw callable uses backend-neutral ports:

- `backend.render.draw_rect(...)`
- `backend.text.draw(...)`

## Controls

- `F1`: toggle built-in debug overlay
- `ESC`: exit

## Next step

- Continue with `config/engine_config_basics` for config-focused scene bootstrap.
