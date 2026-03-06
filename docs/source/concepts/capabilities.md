# Capabilities

This page tracks what is implemented in code today.

Legend:

- `Yes`: implemented and wired
- `Partial`: implemented with known limitations
- `No`: not implemented yet

| Capability | Core | Pygame | Native | Notes |
|---|---|---|---|---|
| Window and event polling | Yes | Yes | Yes | Backend `window` + `input` ports |
| Input snapshot (`InputFrame`) | Yes | Yes | Yes | Keys/buttons/axes/quit state |
| Scene registry and discovery | Yes | N/A | N/A | `SceneRegistry.discover()` |
| Scene stack and overlays | Yes | N/A | N/A | `SceneAdapter` + `ScenePolicy` |
| System pipeline | Yes | N/A | N/A | Ordered `SystemPipeline.step(ctx)` |
| Tick-level command queue | Yes | N/A | N/A | Commands drained each frame |
| Cheat sequence manager | Yes | N/A | N/A | Enqueues commands from key sequences |
| Render pipeline passes | Yes | Yes | Yes | Begin/world/lighting/ui/postfx/end |
| Primitive draw ops (rect/line/circle/poly) | Yes | Yes | Yes | Via backend render ports |
| Texture/sprite draw | Yes | Yes | Yes | Native currently ignores texture rotation |
| Text render and measure | Yes | Yes | Yes | Backend text ports |
| Audio load/play | Yes | Yes | Yes | Runtime adapter calls backend audio |
| Virtual resolution and viewport transforms | Yes | Yes | Yes | Window service + backend transform |
| Capture: screenshots | Yes | Yes | Yes | `CaptureService.screenshot()` |
| Capture: replay record/playback | Yes | Yes | Yes | Input stream serialization |
| Capture: video frame sequence | Yes | Yes | Yes | Post-render frame capture |
| Video encoding to MP4 | Partial | Partial | Partial | Requires `ffmpeg` on PATH |
| Profiler/frame timing reports | Yes | Yes | Yes | `FrameTimer` and reporting |

## Known limitations

- Backend parity exists for core rendering/capture APIs, but game-level
  feature parity still depends on each game and asset pipeline.
- Capability coverage is broader than tutorial coverage; some features exist in
  core code before dedicated tutorials are added.
