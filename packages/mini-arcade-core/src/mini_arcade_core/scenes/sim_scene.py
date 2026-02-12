"""
Simulation scene protocol module.
Defines the SimScene protocol for simulation scenes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, TypeVar

from mini_arcade_core.backend.backend import Backend
from mini_arcade_core.engine.render.packet import DrawOp, RenderPacket
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.systems.system_pipeline import SystemPipeline

if TYPE_CHECKING:
    from mini_arcade_core.engine.commands import CommandQueue

# pylint: disable=invalid-name
TWorld = TypeVar("TWorld")
TIntent = TypeVar("TIntent")
TContext = TypeVar("TContext", bound="BaseTickContext")
# pylint: enable=invalid-name


class BaseWorld:
    """
    Base world data structure.
    Extend this class to define your game's world state.
    """


class BaseIntent:
    """
    Base intent data structure.
    Extend this class to define your game's intent/state changes.
    """


@dataclass
class BaseTickContext(Generic[TWorld, TIntent]):
    """
    Context for a single tick of a SimScene.

    :ivar input_frame: The current input frame.
    :ivar dt: Delta time since last tick.
    :ivar world: The current world state.
    :ivar commands: Command queue for issuing game commands.
    :ivar intent: The current intent/state changes.
    :ivar packet: The render packet to be produced by this tick.
    :ivar draw_ops: Optional list of draw operations for rendering.
    """

    input_frame: InputFrame
    dt: float
    world: TWorld
    commands: CommandQueue
    intent: TIntent | None = None
    packet: RenderPacket | None = None
    draw_ops: list[DrawOp] | None = None


class Drawable(ABC, Generic[TContext]):
    """
    A drawable for scenes that can be drawn.
    """

    @abstractmethod
    def draw(self, backend: Backend, ctx: TContext):
        """
        Draw to the scene.
        """
        raise NotImplementedError


@dataclass(frozen=True)
class DrawCall:
    """
    A draw call for rendering.
    """

    drawable: Drawable[TContext]
    ctx: TContext

    def __call__(self, backend: Backend) -> None:
        self.drawable.draw(backend, self.ctx)


@dataclass
class SimScene(Generic[TContext]):
    """
    Simulation-first scene protocol.
    tick() advances the simulation and returns a RenderPacket for this scene.

    :ivar context: RuntimeContext for this scene.
    """

    context: RuntimeContext
    systems: SystemPipeline[BaseTickContext] | None = None

    def on_enter(self):
        """Called when the scene is entered."""

    def on_exit(self):
        """Called when the scene is exited."""

    def _load_texture(self, path: str) -> int:
        return self.context.services.render.load_texture(path)

    def _get_tick_context(
        self, input_frame: InputFrame, dt: float
    ) -> BaseTickContext:
        """Construct the tick context for the current tick."""
        raise NotImplementedError(
            "Must implement _get_tick_context in subclass"
        )

    def tick(self, input_frame: InputFrame, dt: float) -> RenderPacket:
        """
        Advance the simulation by dt seconds, processing input_frame.

        :param input_frame: Current input frame.
        :type input_frame: InputFrame

        :param dt: Delta time since last tick.
        :type dt: float
        """
        ctx = self._get_tick_context(input_frame, dt)
        self.systems.step(ctx)
        return ctx.packet
