# scene/minimal_scene

## Goal

Understand the smallest useful `SimScene` implementation that still demonstrates:

- scene registration and discovery
- frame-by-frame `tick(input_frame, dt)` execution
- backend-agnostic rendering via `RenderPacket`
- runtime telemetry (backend name, frame, dt, viewport)

## Why this tutorial exists

This is the base scene pattern used before introducing:

- action maps and intent systems
- world/entity simulation
- queued render systems and draw ops
- commands and overlays

If this scene is clear, advanced scene architecture is easier to reason about.

## Source map

- Settings profile:
  `examples/settings/scene/minimal_scene.yml`
- Example builder:
  `examples/catalog/scene/minimal_scene/main.py`
- Runtime scene:
  `examples/catalog/scene/minimal_scene/scenes/scene.py`
- Shared runner:
  `examples/_shared/runner.py`

## Scene lifecycle walkthrough

`MinimalScene` does this:

1. `@register_scene("minimal_scene")`
   registers scene id in auto registry.
2. `__init__(ctx)` initializes local runtime state:
   - `_elapsed`
   - `_frames`
   - `_last_backend_name`
3. `tick(input_frame, dt)`:
   - increments time/frame counters
   - reads runtime config (`self.context.config`)
   - reads viewport telemetry (`window.get_viewport()`)
   - computes animation position (`sin` pulse)
   - returns `RenderPacket.from_ops([draw])`
4. `draw(backend)` callback:
   - records concrete backend class name
   - draws panel + animated rectangle + text diagnostics

This is intentionally one-file, one-scene, no systems.

## Code excerpt

Key parts from
`examples/catalog/scene/minimal_scene/scenes/scene.py`:

```python
SCENE_ID = "minimal_scene"


@register_scene(SCENE_ID)
class MinimalScene(SimScene):
    def __init__(self, ctx: RuntimeContext):
        super().__init__(ctx)
        self._elapsed = 0.0
        self._frames = 0

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        self._elapsed += dt
        self._frames += 1
        vp = self.context.services.window.get_viewport()

        def draw(backend: Backend):
            backend.render.draw_rect(24, 24, 640, 390, color=(0, 0, 0, 220))
            backend.text.draw(
                40, 36, f"frame={self._frames} viewport={vp.window_w}x{vp.window_h}"
            )

        return RenderPacket.from_ops([draw])
```

Why this is important:

- `@register_scene(...)` is how scene IDs become discoverable.
- `tick(...)` is the per-frame simulation/render hook.
- `self.context.services.*` is the runtime service access surface.
- `RenderPacket` is the unit consumed by the render pipeline.

## Config behavior

From `main.py`, this example supports:

- `--backend`
- `--fps`
- `--virtual-width`, `--virtual-height`
- `--window-width`, `--window-height`
- `--enable-profiler`
- `--postfx-enabled`, `--postfx-active`

Config precedence:

1. CLI passthrough overrides
2. `examples/settings/scene/minimal_scene.yml`
3. shared example defaults (`examples/settings/settings.yml`)
4. hardcoded fallback values in builder

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

## What to verify

On screen you should see:

- `backend: <class>` changes between pygame/native runs
- `frame` increments continuously
- `dt` fluctuates near expected frame time
- `fps target` reflects CLI override
- viewport values react to resize

Behavior checks:

1. animated rectangle moves smoothly (tick + dt are active)
2. `F1` toggles debug overlay
3. `ESC` exits cleanly

## How this scales to real games

When moving from this minimal scene to gameplay scenes:

- move local state into `models.py` world dataclass
- replace inline input handling with action-map intent systems
- split rendering into `draw_ops.py` + render system
- move side effects into commands

Reference next levels:

- built-in scene-stack telemetry overlay:
  [debug_overlay_builtin.md](debug_overlay_builtin.md)
- base menu scene pattern:
  [menu_scene_base.md](menu_scene_base.md)
- config-first scene setup:
  [../config/engine_config_basics.md](../config/engine_config_basics.md)
- full game architecture:
  [../create_game.md](../create_game.md)
- scene internals deep dive:
  [../../concepts/scenes_internals.md](../../concepts/scenes_internals.md)

## Common mistakes

- Missing package discovery entry:
  scene is registered but never imported/discovered.
- Forgetting `--pass-through`:
  CLI override flags do not reach the example builder.
- Returning no `RenderPacket`:
  scene runs but displays nothing.
