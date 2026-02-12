"""
SimScene registry for mini arcade core.
Allows registering and creating scenes by string IDs.
"""

from __future__ import annotations

import importlib
import pkgutil
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Protocol

from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.utils import logger

from .autoreg import snapshot

if TYPE_CHECKING:
    from mini_arcade_core.scenes.sim_scene import SimScene


class SceneFactory(Protocol):
    """
    Protocol for scene factory callables.
    """

    def __call__(self, context: RuntimeContext) -> "SimScene": ...


@dataclass
class SceneRegistry:
    """
    Registry for scene factories, allowing registration and creation of scenes by string IDs.
    """

    _factories: Dict[str, SceneFactory]

    @property
    def listed_scene_ids(self) -> list[str]:
        """
        Get a list of all registered scene IDs.

        :return: A list of registered scene IDs.
        :rtype: list[str]
        """
        return list(self._factories.keys())

    def register(self, scene_id: str, factory: SceneFactory):
        """
        Register a scene factory under a given scene ID.

        :param scene_id: The string ID for the scene.
        :type scene_id: str

        :param factory: A callable that creates a SimScene instance.
        :type factory: SceneFactory
        """
        self._factories[scene_id] = factory

    def register_cls(self, scene_id: str, scene_cls: type["SimScene"]):
        """
        Register a SimScene class under a given scene ID.

        :param scene_id: The string ID for the scene.
        :type scene_id: str

        :param scene_cls: The SimScene class to register.
        :type scene_cls: type["SimScene"]
        """

        def return_factory(context: RuntimeContext) -> "SimScene":
            return scene_cls(context)

        self.register(scene_id, return_factory)

    def create(
        self, scene_id: str, context: RuntimeContext
    ) -> "SimScene" | None:
        """
        Create a scene instance using the registered factory for the given scene ID.

        :param scene_id: The string ID of the scene to create.
        :type scene_id: str

        :param game: The Game instance to pass to the scene factory.
        :type game: Game

        :return: A new SimScene instance.
        :rtype: SimScene

        :raises KeyError: If no factory is registered for the given scene ID.
        """
        try:
            scene_factory = self._factories.get(scene_id, None)
            if scene_factory is None:
                logger.warning(f"No factory found for scene_id={scene_id!r}")
                return None
            return self._factories[scene_id](context)
        except KeyError as e:
            raise KeyError(f"Unknown scene_id={scene_id!r}") from e

    def load_catalog(self, catalog: Dict[str, type["SimScene"]]):
        """
        Load a catalog of SimScene classes into the registry.

        :param catalog: A dictionary mapping scene IDs to SimScene classes.
        :type catalog: Dict[str, type["SimScene"]]
        """
        for scene_id, cls in catalog.items():
            self.register_cls(scene_id, cls)

    def discover(self, *packages: str) -> "SceneRegistry":
        """
        Import all modules in a package so @scene decorators run.

        :param packages: The package names to scan for scene modules.
        :type packages: str

        :return: The SceneRegistry instance (for chaining).
        :rtype: SceneRegistry
        """
        for package in packages:
            pkg = importlib.import_module(package)
            if not hasattr(pkg, "__path__"):
                continue

            for mod in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
                importlib.import_module(mod.name)

        self.load_catalog(snapshot())
        return self
