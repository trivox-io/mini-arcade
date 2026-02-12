"""
Scene query adapter implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from mini_arcade_core.engine.scenes.models import SceneEntry
from mini_arcade_core.engine.scenes.scene_manager import SceneAdapter
from mini_arcade_core.runtime.scene.scene_query_port import SceneQueryPort


@dataclass
class SceneQueryAdapter(SceneQueryPort):
    """Adapter that exposes a read-only view of the SceneAdapter manager."""

    _scenes: SceneAdapter

    def visible_entries(self) -> Sequence[SceneEntry]:
        return list(self._scenes.visible_entries())

    def input_entry(self) -> SceneEntry | None:
        return self._scenes.input_entry()

    def stack_summary(self) -> list[str]:
        out: list[str] = []
        for e in self._scenes.visible_entries():
            out.append(f"{e.scene_id} overlay={e.is_overlay}")
        return out
