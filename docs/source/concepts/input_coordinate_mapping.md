# Input Coordinate Mapping Internals

## Purpose

Explain how screen-space input (mouse) is converted into virtual-space
coordinates used by gameplay simulation.

## Core files

- `packages/mini-arcade-core/src/mini_arcade_core/runtime/input/input_adapter.py`
- `packages/mini-arcade-core/src/mini_arcade_core/runtime/window/window_adapter.py`
- `packages/mini-arcade-core/src/mini_arcade_core/engine/render/viewport.py`
- backend input ports:
  - `packages/mini-arcade-pygame-backend/src/mini_arcade_pygame_backend/ports/input.py`
  - `packages/mini-arcade-native-backend/src/mini_arcade_native_backend/mapping/events.py`

## Mapping pipeline

1. Backend emits mouse events with screen coordinates.
2. `InputAdapter` stores:
   - `mouse_pos`
   - `mouse_delta`
   in `InputFrame`.
3. Scene receives `InputFrame` each tick.
4. Scene calls:
   `services.window.screen_to_virtual(x, y)`.
5. Window adapter:
   - applies logical->drawable ratio
   - applies inverse viewport transform
6. Result is virtual-space coordinate for gameplay logic.

## Mapping math

Given viewport state `(offset_x, offset_y, scale)`:

- `virtual_x = (screen_x - offset_x) / scale`
- `virtual_y = (screen_y - offset_y) / scale`

In `FIT` mode, letterbox bars can produce values outside virtual bounds.
In `FILL` mode, mapping remains valid but visible region is cropped.

## Practical guidance

- run gameplay logic and collisions in virtual coordinates
- treat screen coordinates as presentation/input transport only
- clamp mapped coordinates only when game design requires it
- verify mapping in both `FIT` and `FILL`, and after resize

## Tutorial reference

- `docs/source/tutorials/window/screen_to_virtual_input.md`

