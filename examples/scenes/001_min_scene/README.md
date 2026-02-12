# E00 — Boot + Blank Window

## Goal

Prove the engine boots and runs a scene loop.

## What you’ll build

A minimal scene that:

- opens a window
- clears the screen each frame (clear color)
- stays responsive (resize, close)
- exits cleanly on close / ESC

## Concepts taught

- runtime boot
- scene selection / registration
- main loop basics
- backend init + graceful shutdown

## Acceptance criteria

- runs on **native** and **pygame** backends
- window opens and stays responsive
- clean exit on close / ESC

## Run

```bash
mini-arcade run --example 001_min_scene
