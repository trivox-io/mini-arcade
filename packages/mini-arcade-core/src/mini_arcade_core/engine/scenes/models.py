"""
Models for scene management in the engine.
"""

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade_core.scenes.sim_scene import SimScene


@dataclass(frozen=True)
class ScenePolicy:
    """
    Controls how a scene behaves in the scene stack.

    blocks_update: if True, scenes below do not tick/update (pause modal)
    blocks_input:  if True, scenes below do not receive input
    is_opaque:     if True, scenes below are not rendered
    receives_input: if True, scene can receive input
    """

    blocks_update: bool = False
    blocks_input: bool = False
    is_opaque: bool = False
    receives_input: bool = True


@dataclass(frozen=True)
class SceneEntry:
    """
    An entry in the scene stack.

    :ivar scene_id (str): Identifier of the scene.
    :ivar scene (SimScene): The scene instance.
    :ivar is_overlay (bool): Whether the scene is an overlay.
    :ivar policy (ScenePolicy): The scene's policy.
    """

    scene_id: str
    scene: SimScene
    is_overlay: bool
    policy: ScenePolicy


@dataclass(frozen=True)
class StackItem:
    """
    An item in the scene stack.

    :ivar entry (SceneEntry): The scene entry.
    """

    entry: SceneEntry
