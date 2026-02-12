"""
Simulation scene protocol module.
Defines the SimScene protocol for simulation scenes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, TypeVar, Type

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
    Base type for scene world state.

    The world is the single object that represents *everything the scene owns*:
    - gameplay state (entities, score, cooldowns, flags)
    - simulation variables (timers, direction, RNG state if needed)
    - cached runtime resources (texture ids, sound ids, animations)
    - debug/UI overlay state

    Define one world dataclass per scene by inheriting from this class.
    The engine will create it during scene init and provide it to systems each tick.
    """


class BaseIntent:
    """
    Base type for scene intent.

    Intent is a per-frame snapshot produced by the input layer and consumed by
    simulation systems. It should:
    - be independent from raw device events (keyboard/gamepad/mouse)
    - use normalized values (e.g. axis -1..+1, booleans for actions)
    - represent desired actions for *this tick only* (not persistent state)

    Scenes define their own intent dataclass inheriting from this base.
    """


@dataclass
class BaseTickContext(Generic[TWorld, TIntent]):
    """
    Per-tick execution context passed through a SimScene pipeline.

    This is the "shared envelope" for one simulation tick: input snapshot + timing,
    the mutable world state, an outbox for commands, and the per-tick intent and
    render output produced by systems.

    :ivar input_frame: Snapshot of raw/normalized input for this tick.
    :ivar dt: Delta time (seconds) since previous tick.
    :ivar world: Scene-owned world state (usually mutated during the tick).
    :ivar commands: Queue of commands/events emitted by systems.
    :ivar intent: Optional intent snapshot for this tick (produced by input system).
    :ivar packet: Optional render packet produced for this tick.
    :ivar draw_ops: Optional immediate draw operations (debug/overlay/utility).
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
class SimScene(Generic[TContext, TWorld]):
    """
    Simulation-first scene base.

    Lifecycle:
      - __init__(RuntimeContext): constructs the scene container
      - on_enter(): allocate resources, build world, register systems
      - tick(input_frame, dt): build per-tick context, run systems, return RenderPacket

    Subclasses typically provide:
      - build_pipeline() OR register systems in on_enter()
      - build_world() (often in on_enter when window size/assets are needed)

    :ivar context: RuntimeContext for this scene.
    :ivar systems: System pipeline
    :ivar world: Scene world, often set in on_enter
    :tick_context_type: Type of the tick context
    """

    context: RuntimeContext
    systems: SystemPipeline[TContext]
    world: TWorld

    # 👇 each scene sets this
    tick_context_type: Type[TContext] | None = None

    def __init__(self, ctx: RuntimeContext):
        self.context = ctx
        self.systems = self.build_pipeline()

    def build_pipeline(self) -> SystemPipeline[TContext]:
        """
        Return an empty pipeline by default; scenes can override.

        :return: Empty pipeline
        :rtype: SystemPipeline[TContext]
        """
        return SystemPipeline[TContext]()

    def on_enter(self):
        """Called when the scene becomes active (safe place to create world & add systems)."""

    def on_exit(self):
        """Called when the scene stops being active (cleanup optional)."""

    def _load_texture(self, path: str) -> int:
        return self.context.services.render.load_texture(path)

    def _get_tick_context(
        self, input_frame: InputFrame, dt: float
    ) -> TContext:
        """Construct the tick context for the current tick."""
        if self.tick_context_type is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} must set tick_context_type "
                "or override _get_tick_context()."
            )
        return self.tick_context_type(
            input_frame=input_frame,
            dt=dt,
            world=self.world,
            commands=self.context.command_queue,
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

        if ctx.packet is None:
            raise RuntimeError(
                f"{self.__class__.__name__} produced no RenderPacket. "
                "Did you forget to add a render system that sets ctx.packet?"
            )
        return ctx.packet
