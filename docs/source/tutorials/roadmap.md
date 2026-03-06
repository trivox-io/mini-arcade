# Tutorials roadmap

This roadmap tracks grouped tutorial coverage for `examples/catalog/`.

Status legend:

- `DONE`: implemented and runnable
- `WIP`: in progress
- `TODO`: planned

## Roadmap model

- Tutorials are grouped by capability, not fixed numeric sequence.
- Canonical tutorial IDs are slugs (`group/example`).
- Display order can change without renaming content.
- Every tutorial page should include a step-by-step guide.

## Planned groups

### Group 0: Configuration (engine-first)

- `config/engine_config_basics` (`WIP`)
- `config/backend_swap` (`DONE`)

### Group A: Scene stack core

- `scene/minimal_scene` (`TODO`)
- `scene/debug_overlay_builtin` (`TODO`)
- `scene/menu_scene_base` (`TODO`)
- `scene/change_scene` (`TODO`)
- `scene/pause_overlay_policy` (`TODO`)

### Group B: Entities and shapes

- `entity/base_entity_from_dict` (`TODO`)
- `entity/shape_primitives_gallery` (`TODO`)
- `entity/z_index_and_layer_intuition` (`TODO`)

### Group C: Window, viewport, resize

- `window/virtual_resolution_basics` (`TODO`)
- `window/fit_vs_fill` (`TODO`)
- `window/resize_reflow` (`TODO`)
- `window/screen_to_virtual_input` (`TODO`)

### Group D: Input and systems

- `systems/input_frame_visualizer` (`TODO`)
- `systems/action_map_variants` (`TODO`)
- `systems/phases_and_order` (`TODO`)
- `systems/pause_intent_builtin` (`TODO`)
- `systems/animation_tick_builtin` (`TODO`)
- `systems/cull_viewport_builtin` (`TODO`)

### Group E: Commands and cheats

- `commands/custom_scene_commands` (`TODO`)
- `commands/scene_stack_commands` (`TODO`)
- `commands/cheat_sequences` (`TODO`)
- `commands/effect_and_debug_hotkeys` (`TODO`)

### Group F: Render pipeline passes

- `render/world_pass` (`TODO`)
- `render/lighting_pass` (`TODO`)
- `render/ui_pass` (`TODO`)
- `render/effects_layer_pass` (`TODO`)
- `render/postfx_stack` (`TODO`)
- `render/frame_begin_end` (`TODO`)

### Group G: Runtime services

- `runtime/audio_load_play` (`TODO`)
- `runtime/audio_loop_and_volume` (`TODO`)
- `runtime/files_write_text` (`TODO`)
- `runtime/files_write_bytes` (`TODO`, after adapter verification)

### Group H: Capture, replay, bus

- `capture/screenshot_hotkey` (`TODO`)
- `capture/video_record_toggle` (`TODO`)
- `capture/replay_record_and_play` (`TODO`)
- `capture/event_bus_notifications` (`TODO`)

### Group I: Integration

- `integration/micro_game_slice` (`TODO`)

## Deferred until stabilized

- Movement-first progression as core tutorial path
- Advanced physics tuning topics
- Collision deep-dive as baseline track

## Notes

- Keep docs pages aligned with runnable example IDs.
- Keep one primary concept per tutorial page.
- Include next-step links so the grouped path still feels guided.
