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

- `create_game` (`DONE`)
- `config/engine_config_basics` (`DONE`)
- `config/backend_swap` (`DONE`)

### Group A: Scene stack core

- `scene/minimal_scene` (`DONE`)
- `scene/change_scene` (`DONE`)
- `scene/menu_scene_base` (`DONE`)
- `scene/pause_overlay_policy` (`DONE`)
- `scene/debug_overlay_builtin` (`DONE`)

### Group B: Window, viewport, resize

- `window/virtual_resolution_basics` (`DONE`)
- `window/fit_vs_fill` (`DONE`)
- `window/resize_reflow` (`DONE`)
- `window/screen_to_virtual_input` (`DONE`)

### Group C: Entities, shapes, sprites, animation

- `entity/base_entity_from_dict` (`DONE`)
- `entity/shape_primitives_gallery` (`DONE`)
- `entity/z_index_and_layer_intuition` (`DONE`)
- `entity/sprite_texture_basics` (`DONE`)
- `entity/animation_frames_basics` (`DONE`)

### Group D: Input and systems

- `systems/input_frame_visualizer` (`DONE`)
- `systems/action_map_variants` (`DONE`)
- `systems/phases_and_order` (`DONE`)
- `systems/pause_intent_builtin` (`DONE`)
- `systems/animation_tick_builtin` (`DONE`)
- `systems/cull_viewport_builtin` (`DONE`)

### Group E: Commands and cheats

- `commands/custom_scene_commands` (`DONE`)
- `commands/scene_stack_commands` (`DONE`)
- `commands/cheat_sequences` (`DONE`)
- `commands/effect_and_debug_hotkeys` (`DONE`)

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
- `mini-arcade cli examples tour` should follow the implemented roadmap order.
- Keep one primary concept per tutorial page.
- Include next-step links so the grouped path still feels guided.
