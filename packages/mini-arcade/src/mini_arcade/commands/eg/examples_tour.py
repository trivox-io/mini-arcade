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
    Discovers example ids for the tour command based on the presence of main.py files.

    :param examples_parent: The parent directory where examples are located.
    :type examples_parent: Path
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
        Discovers example ids by looking for main.py files under the examples parent directory.

        :return: A list of example ids discovered.
        :rtype: list[str]
        :raises ValueError: If the examples parent directory does not exist or is not a directory.
        """
        if not self.base.exists() or not self.base.is_dir():
            raise ValueError(
                f"Examples parent directory does not exist or is not a directory: {self.base}"
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
    Simple event bus for the examples tour, allowing subscribers to listen to tour events.
    """

    def __init__(self):
        self._subscribers: dict[str, list[Callable[..., None]]] = {}

    def on(self, event_type: str, handler: Callable[..., None]):
        """
        Subscribes a handler to a specific event type.

        :param event_type: The type of event to subscribe to.
        :type event_type: str
        :param handler: The function to call when the event is emitted.
        :type handler: Callable[..., None]
        """
        self._subscribers.setdefault(event_type, []).append(handler)

    def emit(self, event_type: str, **kwargs):
        """
        Emits an event to all subscribed handlers.

        :param event_type: The type of event to emit.
        :type event_type: str
        :param kwargs: Additional keyword arguments to pass to the handlers.
        :type kwargs: dict
        """
        for handler in self._subscribers.get(event_type, []):
            handler(**kwargs)


class TourEvents:
    """
    Defines event types for the examples tour.

    :cvar SESSION_STARTED: Emitted when the tour session starts, with total examples and their ids.
    :cvar EXAMPLE_STARTED: Emitted when an example starts, with index, total, example_id, and command.
    :cvar EXAMPLE_FINISHED: Emitted when an example finishes, with index, total, example_id, and exit_code.
    :cvar EXAMPLE_FAILED: Emitted when an example fails, with index, total, example_id, and error message.
    :cvar SESSION_FINISHED: Emitted when the tour session finishes, with total examples, passed count, failed count, and whether it was stopped early.
    """

    SESSION_STARTED = "session_started"
    EXAMPLE_STARTED = "example_started"
    EXAMPLE_FINISHED = "example_finished"
    EXAMPLE_FAILED = "example_failed"
    SESSION_FINISHED = "session_finished"


class ConsoleTourReporter:
    """
    Example tour reporter that listens to tour events and prints updates to the console.

    :param bus: The event bus to listen to.
    :type bus: ExampleTourBus
    """

    def __init__(self, bus: ExampleTourBus):
        bus.on(TourEvents.SESSION_STARTED, self._on_session_started)
        bus.on(TourEvents.EXAMPLE_STARTED, self._on_example_started)
        bus.on(TourEvents.EXAMPLE_FINISHED, self._on_example_finished)
        bus.on(TourEvents.EXAMPLE_FAILED, self._on_example_failed)
        bus.on(TourEvents.SESSION_FINISHED, self._on_session_finished)

    def _on_session_started(self, *, total: int, examples: list[str]):
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
    ):
        print(f"[{index}/{total}] Starting: {example_id}")
        print(f"cmd={' '.join(cmd.split()) if isinstance(cmd, str) else cmd}")

    def _on_example_finished(
        self,
        *,
        index: int,
        total: int,
        example_id: str,
        exit_code: int,
    ):
        print(f"[{index}/{total}] Finished: {example_id} (exit={exit_code})")

    def _on_example_failed(
        self,
        *,
        index: int,
        total: int,
        example_id: str,
        error: str,
    ):
        print(f"[{index}/{total}] Failed: {example_id} ({error})")

    def _on_session_finished(
        self,
        *,
        total: int,
        passed: int,
        failed: int,
        stopped: bool,
    ):
        status = "stopped early" if stopped else "completed"
        print(
            f"Examples tour {status}: total={total}, passed={passed}, "
            f"failed={failed}"
        )


@dataclass(frozen=True)
class ExampleTourContext:
    """
    Context information for an example being run in the tour.

    :ivar parent_dir (Path | None): The parent directory where the example is located.
    :ivar example_id (str | None): The id of the example being run.
    :ivar index (int | None): The index of the example in the tour (1-based).
    :ivar total (int | None): The total number of examples in the tour.
    """

    parent_dir: Path | None = None
    example_id: str | None = None
    index: int | None = None
    total: int | None = None
