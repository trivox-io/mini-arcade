# E00.2 — Hello Overlay

## Goal

Prove the engine can render a **debug/UI overlay** consistently across backends, independent of world rendering.

## What you’ll build

A minimal scene that:

- renders a small overlay in the top-left corner
- displays:
  - scene name / id
  - backend name
  - FPS (smoothed)
  - frame time in ms (smoothed)
- toggles the overlay on/off with a key

## Concepts taught

- UI pass vs world pass (overlay drawn last / “on top”)
- text rendering (`backend.text.draw`, `backend.text.measure`)
- input edge triggers (one-shot key presses)
- basic perf metrics (FPS / frame time) + smoothing (EMA)

## Acceptance criteria

- overlay renders consistently across backends
- overlay can be toggled on/off with a key (default: **F1**)
- scene stays responsive and exits cleanly (close window / ESC handled by runtime)

## Controls

- **F1** — Toggle overlay

## Run

```bash
mini-arcade run --example 002_hello_overlay
```

## Notes (important)

Right now, the shared example runner (`examples/_shared/run_example.py`) **does not forward CLI passthrough args** to `build_example()`, and `build_example()` in this example **hardcodes** the backend factory.

That means flags like `--backend native` **won’t do anything yet** unless you implement passthrough parsing + forwarding, or you manually change the backend in `build_example()`.

Suggested next step:

- parse args in the shared runner and call `run_example(example_id, **kwargs)`
- then let each example’s `build_example(**kwargs)` choose the backend based on `kwargs["backend"]`
