"""
Example tour discovery and reporting utilities.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

ROADMAP_EXAMPLE_ORDER: tuple[str, ...] = (
    "config/engine_config_basics",
    "config/backend_swap",
    "scene/minimal_scene",
    "scene/change_scene",
    "scene/menu_scene_base",
    "scene/pause_overlay_policy",
    "scene/debug_overlay_builtin",
    "window/virtual_resolution_basics",
    "window/fit_vs_fill",
    "window/resize_reflow",
    "window/screen_to_virtual_input",
    "entity/base_entity_from_dict",
    "entity/shape_primitives_gallery",
    "entity/z_index_and_layer_intuition",
    "entity/sprite_texture_basics",
    "entity/animation_frames_basics",
)


class ExampleTourDiscoverer:
    """
    Discover example ids for the tour command from ``main.py`` files.
    """

    def __init__(self, examples_parent: Path):
        self.base = examples_parent.resolve()

    def _sort_example_ids(self, ids: list[str]) -> list[str]:
        order_index = {
            example_id: index
            for index, example_id in enumerate(ROADMAP_EXAMPLE_ORDER)
        }

        return sorted(
            ids,
            key=lambda example_id: (
                0 if example_id in order_index else 1,
                order_index.get(example_id, len(ROADMAP_EXAMPLE_ORDER)),
                example_id,
            ),
        )

    def discover_example_ids(self) -> list[str]:
        """
        Discover example ids under the configured examples parent directory.
        """
        if not self.base.exists() or not self.base.is_dir():
            raise ValueError(
                "Examples parent directory does not exist or is not a "
                f"directory: {self.base}"
            )

        ids: list[str] = []
        for main_py in sorted(
            self.base.rglob("main.py"),
            key=lambda p: str(p).lower(),
        ):
            rel = str(main_py.parent.resolve().relative_to(self.base))
            rel_id = rel.replace("\\", "/").strip("/")
            if rel_id:
                ids.append(rel_id)

        deduped = list(dict.fromkeys(ids))
        return self._sort_example_ids(deduped)


class ExampleTourBus:
    """
    Minimal event bus used by the examples tour reporter flow.
    """

    def __init__(self):
        self._subscribers: dict[str, list[Callable[..., None]]] = {}

    def on(self, event_type: str, handler: Callable[..., None]) -> None:
        """
        Subscribe one handler to one event type.
        """
        self._subscribers.setdefault(event_type, []).append(handler)

    def emit(self, event_type: str, **kwargs) -> None:
        """
        Emit one event to all subscribed handlers.
        """
        for handler in self._subscribers.get(event_type, []):
            handler(**kwargs)


class TourEvents:
    """
    Event names used by the examples tour.
    """

    SESSION_STARTED = "session_started"
    EXAMPLE_STARTED = "example_started"
    EXAMPLE_FINISHED = "example_finished"
    EXAMPLE_FAILED = "example_failed"
    SESSION_FINISHED = "session_finished"


class ConsoleTourReporter:
    """
    Print tour progress by listening to bus events.
    """

    def __init__(self, bus: ExampleTourBus):
        bus.on(TourEvents.SESSION_STARTED, self._on_session_started)
        bus.on(TourEvents.EXAMPLE_STARTED, self._on_example_started)
        bus.on(TourEvents.EXAMPLE_FINISHED, self._on_example_finished)
        bus.on(TourEvents.EXAMPLE_FAILED, self._on_example_failed)
        bus.on(TourEvents.SESSION_FINISHED, self._on_session_finished)

    def _on_session_started(self, *, total: int, examples: list[str]) -> None:
        print(f"Starting examples tour ({total} examples).")
        if examples:
            print("Order:")
            for idx, example_id in enumerate(examples, start=1):
                print(f"  {idx}. {example_id}")

    def _on_example_started(
        self,
        *,
        index: int,
        total: int,
        example_id: str,
        cmd: str,
    ) -> None:
        print(f"[{index}/{total}] Starting: {example_id}")
        print(f"cmd={' '.join(cmd.split()) if isinstance(cmd, str) else cmd}")

    def _on_example_finished(
        self,
        *,
        index: int,
        total: int,
        example_id: str,
        exit_code: int,
    ) -> None:
        print(f"[{index}/{total}] Finished: {example_id} (exit={exit_code})")

    def _on_example_failed(
        self,
        *,
        index: int,
        total: int,
        example_id: str,
        error: str,
    ) -> None:
        print(f"[{index}/{total}] Failed: {example_id} ({error})")

    def _on_session_finished(
        self,
        *,
        total: int,
        passed: int,
        failed: int,
        stopped: bool,
    ) -> None:
        status = "stopped early" if stopped else "completed"
        print(
            f"Examples tour {status}: total={total}, passed={passed}, "
            f"failed={failed}"
        )


@dataclass(frozen=True)
class ExampleTourContext:
    """
    Context for one example execution within a tour.
    """

    parent_dir: Path | None = None
    example_id: str | None = None
    index: int | None = None
    total: int | None = None
