# Architecture

Mini Arcade is a monorepo with independently published packages that evolve together.

The core idea is a simulation-first engine with backend adapters, scene-driven gameplay,
and an explicit render/capture pipeline.

## Mental model

At runtime:

- `GameConfig` defines the initial scene, backend, fps, virtual resolution, and postfx.
- `SceneRegistry` discovers and registers scene factories.
- `Game` builds managers and runtime services around a selected backend.
- `EngineRunner` executes the frame loop.
- Scenes produce `RenderPacket` objects; render passes consume `FramePacket` wrappers.
- Capture records input streams (replay) and optional video frames.

## Package map

- `mini-arcade`
  User-facing package: CLI + runner modules for launching games/examples.
- `mini-arcade-core`
  Engine runtime: scenes, systems, loop, commands, rendering, services, spaces.
- `mini-arcade-pygame-backend`
  `Backend` protocol implementation using pygame.
- `mini-arcade-native-backend`
  `Backend` protocol implementation using native SDL2 (`pybind11`).

```{mermaid}
flowchart TD
  subgraph Content[Apps and Content]
    G[Games]
    E[Examples]
  end

  subgraph Product[mini-arcade]
    CLI[CLI and Runner]
  end

  subgraph Core[mini-arcade-core]
    CFG[GameConfig]
    GAME[Game]
    MGR[Managers]
    SVC[RuntimeServices]
    LOOP[EngineRunner]
    SCN[SceneAdapter + SceneRegistry]
    RP[RenderPipeline]
    CAP[CaptureService]
  end

  subgraph Backends[Backends]
    PYG[pygame]
    NAT[native SDL2]
  end

  G --> CLI
  E --> CLI
  CLI --> CFG
  CFG --> GAME
  GAME --> MGR
  GAME --> SVC
  GAME --> LOOP
  MGR --> SCN
  LOOP --> SCN
  LOOP --> RP
  LOOP --> CAP

  GAME --> PYG
  GAME --> NAT
  PYG --> SVC
  NAT --> SVC
```

## Core runtime objects

### `Game`

`Game` is the composition root for a running session. It wires:

- managers (`cheats`, `command_queue`, `scenes`)
- runtime services (`window`, `audio`, `files`, `capture`, `input`, `render`, `scenes`)
- postfx registry and stack
- loop hooks (`DefaultGameHooks`)

### Managers

- `SceneAdapter`: stack operations (`change`, `push`, `pop`, `remove_scene`, `quit`)
- `CommandQueue`: tick-level command outbox
- `CheatManager`: key-sequence matcher that enqueues commands

### Runtime services

`RuntimeServices` exposes ports/adapters for:

- window
- audio
- files
- capture
- input
- render
- scene queries

### Scenes and systems

Scenes are `SimScene` subclasses. A scene tick:

1. builds a typed tick context (`BaseTickContext`-derived)
2. runs `SystemPipeline.step(ctx)`
3. must set `ctx.packet` and return a `RenderPacket`

The world state is scene-owned (`scene.world`), while side effects are emitted through commands/services.

## Frame lifecycle (actual loop order)

`EngineRunner.run()` performs this order per frame:

1. Poll backend events.
2. Apply loop hooks (`DefaultGameHooks`) for resize/debug hotkeys.
3. Build `InputFrame` from events, or consume replay input if replay playback is active.
4. If quit is requested, stop loop.
5. Resolve input-focused scene (`input_entry`).
6. Tick update scenes:
   - input scene receives full `InputFrame`
   - other updating scenes receive neutral input for this frame
7. Build `CommandContext` (services + managers + settings + resolved world).
8. Process cheats and enqueue commands.
9. Drain and execute command queue.
10. Build visible `FramePacket` list from scene stack.
11. Build `RenderContext` and run `RenderPipeline` passes.
12. Record video frame if capture is active.
13. Sleep to honor target fps.
14. Emit profiler report (if enabled) and increment `frame_index`.

On exit, scene stack is cleaned (`scenes.clean()`).

```{mermaid}
sequenceDiagram
  participant CLI as mini-arcade
  participant G as Game
  participant ER as EngineRunner
  participant BK as Backend
  participant SC as SceneAdapter
  participant CQ as CommandQueue
  participant RP as RenderPipeline
  participant CP as CaptureService

  CLI->>G: build config + registry + backend
  G->>ER: run loop

  loop each frame
    ER->>BK: poll events
    ER->>ER: hooks.on_events(events)
    ER->>ER: build InputFrame (or replay input)
    ER->>SC: tick update entries
    ER->>CQ: cheats enqueue commands
    ER->>CQ: drain and execute
    ER->>SC: collect visible FramePackets
    ER->>RP: render_frame(backend, context, packets)
    ER->>CP: record_video_frame(frame_index)
  end

  ER->>SC: clean scene stack
```

## Scene stack policy

Scene stack behavior is policy-driven (`ScenePolicy` on each stack entry):

- render visibility: render from highest opaque scene upward
- update propagation: top-down until a scene blocks updates
- input routing: top-most eligible scene receives input, respecting blockers

This gives overlays (pause/menu/debug) explicit control over update/input/render behavior.

## Render model

Rendering is packet-based:

- scene tick returns `RenderPacket(ops, meta)`
- runner wraps packets into `FramePacket(scene_id, is_overlay, packet)`
- pipeline executes ordered passes:
  - `BeginFramePass`
  - `WorldPass`
  - `LightingPass`
  - `UIPass`
  - `PostFXPass`
  - `EndFramePass`

Layered rendering can be driven via `packet.meta["pass_ops"]` with keys like
`world`, `lighting`, `ui`, `effects`.

## Input, intent, commands

The engine separates concerns:

- `InputAdapter` turns backend events into `InputFrame` snapshots.
- scene input systems map raw input to scene-specific intent.
- systems mutate world state using intent.
- side effects (scene transitions, capture toggles, quit, effect toggles) are emitted as commands.

This keeps gameplay logic testable and mostly backend-agnostic.

## Capture and replay

`CaptureService` handles:

- screenshots
- replay record/playback (`InputFrame` stream)
- video frame capture + optional async encoding

Video capture is invoked after render in the frame loop.

## Repo layout

```text
mini-arcade/
|- packages/
|- games/
|- examples/
`- docs/
```

## Why monorepo

- one architecture across core, backends, examples, and games
- shared tooling and CI
- coordinated versioning and releases
- docs tied directly to implementation changes
