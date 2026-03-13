"""
Built-in visual runner for system lab cases.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import importlib.util
import os
from pathlib import Path
import sys
import time
from typing import Any

from mini_arcade.modules.backend_loader import BackendLoader
from mini_arcade_core import run_game
from mini_arcade_core.backend.keys import Key
from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.bootstrap import scene_viewport
from mini_arcade_core.scenes.sim_scene import DrawCall, SimScene, SubmitRenderQueue
from mini_arcade_core.scenes.systems.base_system import BaseSystem
from mini_arcade_core.scenes.systems.builtins import ConfiguredActionIntentSystem
from mini_arcade_core.scenes.systems.phases import SystemPhase

from .registry import BaseSystemLabCase, SystemLabVisualSpec

_ACTIVE_CASE: BaseSystemLabCase | None = None
_ACTIVE_SPEC: SystemLabVisualSpec | None = None
_ACTIVE_MODULE_NAMES: tuple[str, ...] = ()


def _deep_merge(base: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in overrides.items():
        current = merged.get(key)
        if isinstance(current, dict) and isinstance(value, dict):
            merged[key] = _deep_merge(current, value)
            continue
        merged[key] = value
    return merged


def _require_active_case() -> BaseSystemLabCase:
    if _ACTIVE_CASE is None:
        raise RuntimeError("No active system lab case is registered")
    return _ACTIVE_CASE


def _require_active_spec() -> SystemLabVisualSpec:
    if _ACTIVE_SPEC is None:
        raise RuntimeError("No active system lab visual spec is registered")
    return _ACTIVE_SPEC


def _require_active_module_names() -> tuple[str, ...]:
    if not _ACTIVE_MODULE_NAMES:
        return ()
    return _ACTIVE_MODULE_NAMES


def _build_backend_config(spec: SystemLabVisualSpec) -> dict[str, Any]:
    window_size = spec.window_size or spec.virtual_resolution
    return {
        "provider": str(spec.backend_provider).strip().lower() or "pygame",
        "window": {
            "width": int(window_size[0]),
            "height": int(window_size[1]),
            "title": spec.title,
            "resizable": True,
        },
        "renderer": {
            "background_color": list(spec.background_color),
        },
        "audio": {
            "enable": False,
        },
    }


def _build_gameplay_config(spec: SystemLabVisualSpec) -> dict[str, Any]:
    base = {
        "debug_overlay": {
            "enabled": bool(spec.debug_overlay_enabled),
            "start_visible": bool(spec.debug_overlay_start_visible),
            "title": spec.debug_overlay_title,
            "sections": list(spec.debug_overlay_sections),
        },
        "scenes": {
            spec.scene_id: {
                "escape": {
                    "command": "quit",
                }
            }
        },
    }
    return _deep_merge(base, dict(spec.gameplay_overrides))


def _source_path_for_module_file(file_name: str | None) -> Path | None:
    if not file_name:
        return None

    path = Path(file_name)
    if path.suffix in {".pyc", ".pyo"}:
        try:
            path = Path(importlib.util.source_from_cache(str(path)))
        except ValueError:
            pass
    return path.resolve() if path.exists() else None


def _discover_watch_paths(module_names: tuple[str, ...]) -> tuple[Path, ...]:
    prefixes: set[str] = set()
    for module_name in module_names:
        normalized = str(module_name).strip()
        if not normalized:
            continue
        prefixes.add(normalized)
        if "." in normalized:
            prefixes.add(normalized.rsplit(".", 1)[0])

    watch_paths: set[Path] = set()
    for loaded_name, module in sys.modules.items():
        if not any(
            loaded_name == prefix or loaded_name.startswith(f"{prefix}.")
            for prefix in prefixes
        ):
            continue
        module_file = getattr(module, "__file__", None)
        source_path = _source_path_for_module_file(module_file)
        if source_path is not None:
            watch_paths.add(source_path)

    return tuple(sorted(watch_paths))


def _snapshot_watch_state(paths: tuple[Path, ...]) -> dict[Path, int]:
    state: dict[Path, int] = {}
    for path in paths:
        try:
            state[path] = path.stat().st_mtime_ns
        except FileNotFoundError:
            state[path] = -1
    return state


def _watch_state_changed(
    previous_state: dict[Path, int],
    current_state: dict[Path, int],
) -> bool:
    return previous_state != current_state


def _restart_current_process(reason: str) -> None:
    print(f"[system-lab] {reason}; restarting...")
    sys.stdout.flush()
    sys.stderr.flush()
    os.execv(sys.executable, [sys.executable, *sys.argv])


def _build_render_queue_pass_ops(ctx: object) -> dict[str, tuple[object, ...]]:
    layer_map: dict[str, tuple[str, ...]] = {
        "world": ("world", "debug"),
        "lighting": ("lighting",),
        "ui": ("ui",),
        "effects": ("effects", "postfx"),
    }
    render_queue = getattr(ctx, "render_queue")
    out: dict[str, tuple[object, ...]] = {}
    for pass_name, layers in layer_map.items():
        if not render_queue.iter_sorted(layers):
            continue
        out[pass_name] = (
            DrawCall(drawable=SubmitRenderQueue(layers=layers), ctx=ctx),
        )
    return out


@dataclass
class _SystemLabPacketFinalizeSystem(BaseSystem[object]):
    """
    Finalize the packet when a lab system only emits draw ops or render queue data.
    """

    name: str = "system_lab_packet_finalize"
    phase: int = SystemPhase.RENDERING
    order: int = 10_000

    def step(self, ctx: object):
        """Build a packet from queued draw operations when needed."""
        if getattr(ctx, "packet", None) is not None:
            return

        draw_ops = list(getattr(ctx, "draw_ops", None) or [])
        render_queue = getattr(ctx, "render_queue", None)
        if render_queue is None or not render_queue.iter_sorted():
            setattr(ctx, "packet", RenderPacket.from_ops(draw_ops))
            return

        queue_draw = DrawCall(drawable=SubmitRenderQueue(), ctx=ctx)
        setattr(
            ctx,
            "packet",
            RenderPacket.from_ops(
                [queue_draw, *draw_ops],
                pass_ops=_build_render_queue_pass_ops(ctx),
            ),
        )


@dataclass
class _SystemLabHotReloadSystem(BaseSystem[object]):
    """
    Restart the current system-lab process when source files change.
    """

    watch_paths: tuple[Path, ...]
    reload_key: Key | None
    poll_seconds: float
    name: str = "system_lab_hot_reload"
    phase: int = SystemPhase.CONTROL
    order: int = 5

    def __post_init__(self) -> None:
        self._watch_state = _snapshot_watch_state(self.watch_paths)
        self._next_poll_at = time.monotonic() + max(self.poll_seconds, 0.1)

    def step(self, ctx: object) -> None:
        """Restart on `F5` or when any watched module file changes."""
        input_frame = getattr(ctx, "input_frame", None)
        if (
            self.reload_key is not None
            and input_frame is not None
            and self.reload_key in getattr(input_frame, "keys_pressed", ())
        ):
            _restart_current_process(
                f"manual hot reload requested with {self.reload_key.name}"
            )

        now = time.monotonic()
        if now < self._next_poll_at:
            return
        self._next_poll_at = now + max(self.poll_seconds, 0.1)

        current_state = _snapshot_watch_state(self.watch_paths)
        if _watch_state_changed(self._watch_state, current_state):
            _restart_current_process("detected source change")
        self._watch_state = current_state


@register_scene("system_lab_visual")
class SystemLabVisualScene(SimScene[object, object]):
    """
    Generic scene used by the built-in system lab visual runner.
    """

    tick_context_type = None

    def __init__(self, ctx):
        super().__init__(ctx)
        self._lab_step_index = 0
        self.scene_id: str | None = None
        self.world: object | None = None

    def on_enter(self):
        """Create the lab world and install optional visual-runner systems."""
        case = _require_active_case()
        spec = _require_active_spec()
        self.scene_id = spec.scene_id
        self.world = case.build_visual_world(viewport=scene_viewport(self))

        if spec.hot_reload_enabled:
            reload_key = getattr(Key, str(spec.hot_reload_key).upper(), None)
            self.systems.add(
                _SystemLabHotReloadSystem(
                    watch_paths=_discover_watch_paths(
                        _require_active_module_names()
                    ),
                    reload_key=reload_key,
                    poll_seconds=float(spec.hot_reload_poll_seconds),
                )
            )

        if (
            spec.intent_factory is not None
            and spec.controls_scene_key is not None
        ):
            self.systems.add(
                ConfiguredActionIntentSystem(
                    controls=getattr(self.context.settings, "controls", None),
                    scene_key=spec.controls_scene_key,
                    intent_factory=spec.intent_factory,
                    fallback_bindings=spec.input_fallback_bindings,
                    name="system_lab_intent",
                    channel="player_1",
                    write_to_ctx_intent=True,
                )
            )

        self.systems.extend(case.build_visual_systems())
        self.systems.add(_SystemLabPacketFinalizeSystem())

    def _get_tick_context(
        self, input_frame: InputFrame, dt: float
    ) -> object:
        spec = _require_active_spec()
        tick_context_type = spec.tick_context_type
        return tick_context_type(
            input_frame=input_frame,
            dt=dt,
            world=self.world,
            commands=self.context.command_queue,
        )

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        """Advance the visual lab by one frame."""
        self._ensure_capture_controls()
        ctx = self._get_tick_context(input_frame, dt)
        case = _require_active_case()
        case.before_step(
            step_index=self._lab_step_index,
            system=self.systems,
            ctx=ctx,
        )
        self.systems.step(ctx)
        case.after_step(
            step_index=self._lab_step_index,
            system=self.systems,
            ctx=ctx,
        )
        self._lab_step_index += 1

        packet = getattr(ctx, "packet", None)
        if packet is None:
            raise RuntimeError(
                "System lab visual scene produced no RenderPacket"
            )
        return packet

    def debug_overlay_lines(self) -> list[str]:
        """Expose built-in lab diagnostics in the debug overlay."""
        case = _require_active_case()
        lines = [f"lab_case: {case.__class__.__name__}"]
        spec = _require_active_spec()
        if spec.hot_reload_enabled:
            lines.append(f"hot_reload: {spec.hot_reload_key} / auto")
        lines.extend(case.visual_debug_lines(world=self.world))
        return lines


def run_system_lab_visual_case(
    case: BaseSystemLabCase,
    spec: SystemLabVisualSpec,
    *,
    module_names: tuple[str, ...] = (),
    backend_provider_override: str | None = None,
) -> int:
    """
    Run a system lab case using the built-in visual scene.
    """
    global _ACTIVE_CASE  # pylint: disable=global-statement
    global _ACTIVE_SPEC  # pylint: disable=global-statement
    global _ACTIVE_MODULE_NAMES  # pylint: disable=global-statement

    normalized_backend = (
        None
        if backend_provider_override is None
        else str(backend_provider_override).strip().lower()
    )
    if normalized_backend:
        spec = replace(spec, backend_provider=normalized_backend)

    _ACTIVE_CASE = case
    _ACTIVE_SPEC = spec
    _ACTIVE_MODULE_NAMES = tuple(module_names)
    try:
        backend = BackendLoader.load_backend(_build_backend_config(spec))
        run_game(
            engine_config={
                "fps": int(spec.fps),
                "virtual_resolution": list(spec.virtual_resolution),
                "enable_profiler": False,
                "postfx": {
                    "enabled": False,
                    "active": [],
                },
            },
            scene_config={
                "initial_scene": "system_lab_visual",
                "discover_packages": [
                    "mini_arcade.modules.system_lab.visual_runner",
                    "mini_arcade_core.scenes",
                ],
            },
            backend=backend,
            gameplay_config=_build_gameplay_config(spec),
        )
        return 0
    finally:
        _ACTIVE_CASE = None
        _ACTIVE_SPEC = None
        _ACTIVE_MODULE_NAMES = ()


__all__ = ["run_system_lab_visual_case", "SystemLabVisualScene"]
