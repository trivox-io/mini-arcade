# Mini Arcade Examples ROADMAP

> Status legend: `TODO` / `WIP` / `DONE`  
> Current baseline: **Empty Scene exists**

---

## E00 — Bootstrap

### E00.1 Empty Scene (baseline)

- **Status:** DONE
- **Goal:** Prove the engine boots and runs a scene loop.
- **User sees:** Blank window (clear color).
- **Teaches:** runtime boot, scene selection, main loop, render clear.
- **Acceptance criteria:**
  - Runs on **native** and **pygame** backends.
  - Window opens and stays responsive.
  - Clean exit on close / ESC.

### E00.2 Hello Overlay

- **Status:** Done
- **Goal:** Show text/UI drawing and basic debug overlay.
- **User sees:** Scene name, backend name, FPS / frame time.
- **Teaches:** UI pass vs world pass, text drawing, debug toggles.
- **Acceptance criteria:**
  - Overlay renders consistently across backends.
  - Toggle overlay on/off with a key.

---

## E01 — Entities and Primitives (no movement)

### E01.1 Single Shape

- **Status:** TODO
- **Goal:** Spawn one entity with a primitive shape component.
- **User sees:** One rectangle or circle centered on screen.
- **Teaches:** entity creation, position/size, color, draw call basics.
- **Acceptance criteria:**
  - One entity appears in a stable position.
  - Can change shape type via a constant or simple config.

### E01.2 Shape Gallery

- **Status:** TODO
- **Goal:** Display all available primitives in a simple grid layout.
- **User sees:** Grid of shapes (rect, circle, line, etc.) with labels.
- **Teaches:** draw ordering, coordinate system, layout patterns.
- **Acceptance criteria:**
  - Every supported primitive is showcased.
  - Each primitive is labeled (overlay text).

### E01.3 Z-Order and Layers

- **Status:** TODO
- **Goal:** Demonstrate draw order with overlapping primitives.
- **User sees:** Overlapping shapes with clear front/back ordering.
- **Teaches:** layers/z-index, render pipeline order.
- **Acceptance criteria:**
  - At least 3 layers shown.
  - Easy to see which layer is on top.

---

## E02 — Sprites and Assets (static)

### E02.1 Sprite Basics

- **Status:** TODO
- **Goal:** Load and render a sprite/texture.
- **User sees:** A sprite centered (scaled to fit).
- **Teaches:** asset loading, sprite component, scaling, pivot/anchor.
- **Acceptance criteria:**
  - Sprite appears on both backends.
  - Missing asset produces a friendly error.

### E02.2 Sprite Sheet Preview

- **Status:** TODO
- **Goal:** Render multiple frames from a sprite sheet as a grid (no animation yet).
- **User sees:** A grid of frames from one image.
- **Teaches:** texture regions, UV slicing, atlas mental model.
- **Acceptance criteria:**
  - Frame slicing is deterministic and documented.

---

## E03 — Input (no movement)

### E03.1 Input Visualizer

- **Status:** TODO
- **Goal:** Show currently pressed keys and mouse position.
- **User sees:** Key list + mouse coordinates overlay.
- **Teaches:** input system, key mapping parity across backends.
- **Acceptance criteria:**
  - At least arrows/WASD + space visible.
  - Mouse position updates smoothly.

### E03.2 State Toggle Panel

- **Status:** TODO
- **Goal:** Use key presses to toggle simple scene state.
- **User sees:** Background color / primitive type toggles.
- **Teaches:** state management inside a scene.
- **Acceptance criteria:**
  - At least 3 toggles (e.g., bg color, shape type, show overlay).

---

## E04 — Time and Animation (minimal)

### E04.1 Timer Playground

- **Status:** TODO
- **Goal:** Demonstrate delta-time-driven periodic behavior.
- **User sees:** Blinking indicator + counter/timer label.
- **Teaches:** dt, time accumulation, update cadence.
- **Acceptance criteria:**
  - Blink frequency is stable across backends.

### E04.2 Animated Sprite (in-place)

- **Status:** TODO
- **Goal:** Play an animation from frames.
- **User sees:** Animated sprite looping.
- **Teaches:** animation component, FPS, looping, pause/resume.
- **Acceptance criteria:**
  - Toggle pause/resume.
  - Configurable animation FPS.

---

## E05 — Movement and Simple Systems

### E05.1 Velocity Integration

- **Status:** TODO
- **Goal:** Move an entity with a velocity component.
- **User sees:** A shape drifting steadily.
- **Teaches:** position integration, dt usage, system update order.
- **Acceptance criteria:**
  - Deterministic movement for a fixed dt configuration.

### E05.2 Screen Bounds (wrap vs bounce)

- **Status:** TODO
- **Goal:** Demonstrate edge handling strategies.
- **User sees:** Moving shape wraps or bounces at edges.
- **Teaches:** bounds checks, world rules, reusable helpers.
- **Acceptance criteria:**
  - Two modes selectable (wrap/bounce).

### E05.3 Follow Cursor

- **Status:** TODO
- **Goal:** Move towards mouse with smoothing.
- **User sees:** Entity follows cursor with easing.
- **Teaches:** steering behaviors, interpolation, input → world interaction.
- **Acceptance criteria:**
  - Adjustable smoothing factor.

---

## E06 — Collision

### E06.1 Collider Debug View

- **Status:** TODO
- **Goal:** Draw collider outlines and overlap highlight.
- **User sees:** Two shapes with collider outlines; highlight on overlap.
- **Teaches:** collider components, debug draw, collision queries.
- **Acceptance criteria:**
  - A clear “colliding/not colliding” indicator.

### E06.2 Paddle + Ball Micro

- **Status:** TODO
- **Goal:** Minimal Pong interaction without full game rules.
- **User sees:** Ball bounces; paddle blocks.
- **Teaches:** collision response, reflection, simple input-driven paddle.
- **Acceptance criteria:**
  - Ball never tunnels at reasonable speeds (document limits).

---

## E07 — Camera, Viewport, Scaling

### E07.1 Camera Pan (static world)

- **Status:** TODO
- **Goal:** Show a larger world and move the camera.
- **User sees:** Camera pans across a simple scene.
- **Teaches:** camera transform, world vs screen coords.
- **Acceptance criteria:**
  - Camera movement via keys.

### E07.2 Viewport Modes Showcase

- **Status:** TODO
- **Goal:** FIT vs FILL vs Stretch for same scene.
- **User sees:** Same content rendered with different scaling rules.
- **Teaches:** resolution independence, letterbox, safe areas.
- **Acceptance criteria:**
  - Toggle modes at runtime.
  - Mode name displayed on screen.

---

## E08 — Audio (future-ready)

### E08.1 One-shot SFX

- **Status:** TODO
- **Goal:** Play a sound on keypress.
- **User sees/hears:** Simple click/beep on space.
- **Teaches:** audio loading, playback, latency considerations.
- **Acceptance criteria:**
  - Works on supported backends (or clearly documented if not).

### E08.2 Music Loop

- **Status:** TODO
- **Goal:** Loop background music.
- **User sees/hears:** A looping track with volume controls.
- **Teaches:** music vs SFX channels, volume, pause/resume.
- **Acceptance criteria:**
  - Volume up/down keys.

---

## E09 — Capture (engine differentiator)

### E09.1 Screenshot Capture

- **Status:** TODO
- **Goal:** Save screenshots from any example scene.
- **User sees:** On-screen “Saved screenshot” message; file written.
- **Teaches:** capture port, output naming, formats.
- **Acceptance criteria:**
  - Deterministic naming scheme documented.
  - Output folder auto-created.

### E09.2 Frame Capture (image sequence)

- **Status:** TODO
- **Goal:** Capture N frames to an image sequence.
- **User sees:** Progress indicator; files written.
- **Teaches:** frame stepping, deterministic capture, perf considerations.
- **Acceptance criteria:**
  - Fixed-step option for consistent sequences.

### E09.3 Replay Micro (concept)

- **Status:** TODO
- **Goal:** Record inputs or world state and replay deterministically.
- **User sees:** Short record → replay that matches.
- **Teaches:** determinism constraints, tick serialization, playback mode.
- **Acceptance criteria:**
  - Record/replay toggles.
  - Metadata saved (fps, backend, seed).

---

## E10 — Integration Examples (later)

### E10.1 Deja Bounce Tour Example

- **Status:** TODO
- **Goal:** A doc-first walkthrough of the game architecture.
- **User sees:** Links to systems/components used.
- **Teaches:** organizing a full game in Mini Arcade.
- **Acceptance criteria:**
  - Diagram + “where to start” section.

### E10.2 Space Invaders Tour Example

- **Status:** TODO
- **Goal:** Focus on sprites, animation, cooldowns, projectiles.
- **Acceptance criteria:**
  - Clear mapping from mechanics → engine features.

---

## Backlog Notes

- Each example should ship with:
  - a short README-style description (goal, concepts, run commands)
  - expected output screenshot/GIF (later automated via capture)
  - backend parity notes (native vs pygame)
- Docs strategy:
  - Sphinx pages import each example README
  - “Progression path” links to the next example
