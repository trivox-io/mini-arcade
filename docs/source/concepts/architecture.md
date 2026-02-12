# Architecture

Mini Arcade is a monorepo with multiple independently published packages, developed together for a consistent workflow.

## Mental model

Mini Arcade is **simulation-first** and **data-driven** (increasingly).

At runtime:

- A **GameConfig** defines what to run (initial scene, backend, FPS, post-fx, etc.).
- **Scenes are registered** (registry + optional auto-registration).
- The `Game` bootstraps **managers** and **runtime services**.
- The `EngineRunner` drives the loop:
  - polls backend events
  - builds an `InputFrame` (or reads it from replay)
  - ticks the active scene stack (simulation)
  - processes cheats + executes queued commands
  - renders via a render pipeline (passes + packets)
  - records capture outputs (replay / video frames)

### Frame lifecycle (high level)

1. **Poll backend input** → raw events  
2. **Build InputFrame** → keys/buttons/axes + dt + frame_index  
3. **Tick scenes** → systems update pure data (world/entities/components)  
4. **Collect render packets** → scene produces `RenderPacket` / draw ops  
5. **Render pipeline** → passes render packets in order  
6. **Capture hooks** → record input + optional video frame  
7. **Sleep** to maintain target FPS (optional)

---

## Packages

- `mini-arcade`  
  User-facing package: CLI/runner + unified namespace + “run targets”
- `mini-arcade-core`  
  Engine core: scenes/systems/entities/spaces/runtime services, render pipeline
- `mini-arcade-pygame-backend`  
  Backend implementation using pygame
- `mini-arcade-native-backend`  
  Native backend (SDL2) for performance/control

```{mermaid} id="7e5kc8"
flowchart TD
  subgraph Apps["Apps / Content"]
    G[Games<br/>deja-bounce, space-invaders, ...]
    E[Examples<br/>progressive tutorials]
  end

  subgraph Runner["mini-arcade"]
    CLI[Runner + CLI<br/>select target, backend, config]
  end

  subgraph Core["mini-arcade-core"]
    Game[Game<br/>bootstraps managers + services]
    Loop[EngineRunner<br/>main loop]
    Scenes[Scene stack + Registry]
    Sim[Systems + World<br/>data-only simulation]
    Render[RenderPipeline<br/>passes + packets]
    Cap[CaptureService<br/>replay + video frames]
  end

  subgraph Backends["Backends"]
    PYG[pygame backend]
    NAT[native SDL2 backend]
  end

  G --> CLI
  E --> CLI
  CLI --> Game
  Game --> Loop
  Loop --> Scenes
  Scenes --> Sim
  Loop --> Render
  Loop --> Cap

  CLI --> PYG
  CLI --> NAT
  PYG --> Core
  NAT --> Core

  Render --> PYG
  Render --> NAT
  Cap --> PYG
  Cap --> NAT
```

---

## Runtime flow (closer to the actual code)

```{mermaid} id="bjuaqa"
sequenceDiagram
  participant U as User
  participant CLI as mini-arcade (runner/CLI)
  participant G as Game (core)
  participant ER as EngineRunner (core)
  participant BK as Backend (pygame/native)
  participant IN as InputAdapter/Capture
  participant SC as Scene stack
  participant CM as Cheats/Commands
  participant RP as RenderPipeline
  participant CP as CaptureService

  U->>CLI: run target + config (backend, fps, initial_scene)
  CLI->>G: Game(cfg, registry)
  G->>BK: init window/resources (via adapters)
  G->>ER: EngineRunner(game, pipeline, hooks)
  loop each frame
    ER->>BK: poll events
    ER->>IN: build InputFrame (or replay input)
    ER->>SC: tick update entries (systems) -> RenderPacket
    ER->>CM: cheats.process_frame()
    ER->>CM: command_queue.drain().execute(ctx)
    ER->>RP: render_frame(backend, frame_packets)
    ER->>CP: record_video_frame(frame_index)
  end
  BK-->>ER: quit/close
  ER-->>SC: scenes.clean()
```

---

## Where “intents” fit

Scenes typically convert `InputFrame` → **Intent** in an input system (one-shot + held input), then downstream systems make decisions based on that intent.

Example pattern:

- `InputSystem` reads keys → produces `SpaceInvadersIntent`
- gameplay systems read `ctx.intent` and mutate **world data only**
- render system produces draw calls / render ops from world state

This keeps gameplay deterministic and testable.

---

## Repo layout

```text
mini-arcade/
├─ packages/
├─ games/
├─ examples/
└─ docs/
```

## Why a monorepo

- shared tooling and standards (formatting, linting, typing)
- one CI pipeline to validate everything together
- coordinated releases with correct publish order
- unified documentation and learning path

---

### Note on naming (precision)

In the docs above we say “draw calls” sometimes for readability, but in the actual engine the scene typically produces a `RenderPacket`, and the render pipeline consumes a stack of `FramePacket(scene_id, is_overlay, packet)`.
