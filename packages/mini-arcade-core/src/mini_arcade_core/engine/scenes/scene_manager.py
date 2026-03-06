"""
Module providing runtime adapters for window and scene management.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from mini_arcade_core.engine.scenes.models import (
    SceneEntry,
    ScenePolicy,
    StackItem,
)
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.scenes.registry import SceneRegistry
from mini_arcade_core.utils import logger

if TYPE_CHECKING:
    from mini_arcade_core.engine.game import Engine
    from mini_arcade_core.scenes.sim_scene import SimScene


class SceneAdapter:
    """
    Manages multiple scenes (not implemented).
    """

    def __init__(self, registry: SceneRegistry, game: Engine):
        self._registry = registry
        self._stack: List[StackItem] = []
        self._game = game

    @property
    def current_scene(self) -> SimScene | None:
        """
        Get the currently active scene.

        :return: The active Scene instance, or None if no scene is active.
        :rtype: SimScene | None
        """
        return self._stack[-1].entry.scene if self._stack else None

    @property
    def visible_stack(self) -> List[SimScene]:
        """
        Return the list of scenes that should be drawn (base + overlays).
        We draw from the top-most non-overlay scene upward.

        :return: List of visible Scene instances.
        :rtype: List[SimScene]
        """
        return [e.scene for e in self.visible_entries()]

    @property
    def listed_scenes(self) -> List[SimScene]:
        """
        Return all scenes in the stack.

        :return: List of all Scene instances in the stack.
        :rtype: List[SimScene]
        """
        return [item.entry.scene for item in self._stack]

    def change(self, scene_id: str):
        """
        Change the current scene to the specified scene.

        :param scene_id: Identifier of the scene to switch to.
        :type scene_id: str
        """
        self.clean()
        self.push(scene_id, as_overlay=False)

    def push(
        self,
        scene_id: str,
        *,
        as_overlay: bool = False,
        policy: ScenePolicy | None = None,
    ):
        """
        Push a new scene onto the scene stack.

        :param scene_id: Identifier of the scene to push.
        :type scene_id: str

        :param as_overlay: Whether to push the scene as an overlay.
        :type as_overlay: bool
        """
        # default policy based on overlay vs base
        if policy is None:
            # base scenes: do not block anything by default
            policy = ScenePolicy()
        runtime_context = RuntimeContext.from_game(self._game)
        scene = self._registry.create(
            scene_id, runtime_context
        )  # or whatever your factory call is
        if not scene:
            logger.warning(f"Failed to create scene with id={scene_id!r}")
            return
        scene.scene_id = scene_id
        scene.on_enter()

        entry = SceneEntry(
            scene_id=scene_id,
            scene=scene,
            is_overlay=as_overlay,
            policy=policy,
        )
        self._stack.append(StackItem(entry=entry))

    def pop(self) -> SimScene | None:
        """
        Pop the current scene from the scene stack.

        :return: The popped Scene instance, or None if the stack was empty.
        :rtype: SimScene | None
        """
        if not self._stack:
            return
        item = self._stack.pop()
        item.entry.scene.on_exit()

    def clean(self):
        """Clean up all scenes from the scene stack."""
        while self._stack:
            self.pop()

    def quit(self):
        """Quit the game"""
        self._game.quit()

    def visible_entries(self) -> list[SceneEntry]:
        """
        Render from bottom->top unless an opaque entry exists; if so,
            render only from that entry up.

        :return: List of SceneEntry instances to render.
        :rtype: list[SceneEntry]
        """
        entries = [i.entry for i in self._stack]
        # find highest opaque from top down; render starting there
        for idx in range(len(entries) - 1, -1, -1):
            if entries[idx].policy.is_opaque:
                return entries[idx:]
        return entries

    def update_entries(self) -> list[SceneEntry]:
        """
        Tick/update scenes considering blocks_update.
        Typical: pause overlay blocks update below it.

        :return: List of SceneEntry instances to update.
        :rtype: list[SceneEntry]
        """
        vis = self.visible_entries()
        if not vis:
            return []
        out = []
        for entry in reversed(vis):  # top->down
            out.append(entry)
            if entry.policy.blocks_update:
                break
        return list(reversed(out))  # bottom->top order

    def input_entry(self) -> SceneEntry | None:
        """
        Who gets input this frame. If top blocks_input, only it receives input.
        If not, top still gets input (v1 simple). Later you can allow fall-through.

        :return: The SceneEntry that receives input, or None if no scenes are active.
        :rtype: SceneEntry | None
        """
        vis = self.visible_entries()
        if not vis:
            return None

        # If some scene blocks input, only scenes at/above it can receive.
        start_idx = 0
        for idx in range(len(vis) - 1, -1, -1):
            if vis[idx].policy.blocks_input:
                start_idx = idx
                break

        candidates = vis[start_idx:]

        # Pick the top-most candidate that actually receives input.
        for entry in reversed(candidates):
            if entry.policy.receives_input:
                return entry

        return None

    def has_scene(self, scene_id: str) -> bool:
        """
        Check if a scene with the given ID exists in the stack.

        :param scene_id: Identifier of the scene to check.
        :type scene_id: str

        :return: True if the scene exists in the stack, False otherwise.
        :rtype: bool
        """
        return any(item.entry.scene_id == scene_id for item in self._stack)

    def remove_scene(self, scene_id: str):
        """
        Remove a scene with the given ID from the stack.

        :param scene_id: Identifier of the scene to remove.
        :type scene_id: str
        """
        # remove first match from top (overlay is usually near top)
        for i in range(len(self._stack) - 1, -1, -1):
            if self._stack[i].entry.scene_id == scene_id:
                item = self._stack.pop(i)
                item.entry.scene.on_exit()
                return
