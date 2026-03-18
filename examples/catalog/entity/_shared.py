"""
Shared runtime helpers for Group C entity tutorials.
"""

from __future__ import annotations


# isort owns import ordering; pylint misclassifies local packages as third-party.
# pylint: disable=wrong-import-order
from dataclasses import dataclass, field
from typing import Callable, Iterable, cast

from examples._shared.text_layout import draw_text_block, fit_text_block
from mini_arcade_core.engine.entities import BaseEntity
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.scenes.game_scene import GameScene
from mini_arcade_core.scenes.sim_scene import (
    BaseIntent,
    BaseTickContext,
    BaseWorld,
    Drawable,
)
from mini_arcade_core.scenes.systems.base_system import BaseSystem
from mini_arcade_core.scenes.systems.builtins import (
    ConfiguredQueuedRenderSystem,
    KinematicMotionSystem,
    MotionBinding,
    RenderOverlay,
    ViewportConstraintBinding,
    ViewportConstraintSystem,
)
from mini_arcade_core.scenes.systems.phases import SystemPhase


@dataclass
class EntityExampleWorld(BaseWorld):
    """
    Shared world model for entity tutorials.
    """

    viewport: tuple[float, float]
    elapsed: float = 0.0
    frame: int = 0


@dataclass(frozen=True)
class EntityExampleIntent(BaseIntent):
    """
    Empty per-frame intent for examples that do not require input mapping yet.
    """


@dataclass
class EntityExampleTickContext(
    BaseTickContext[EntityExampleWorld, EntityExampleIntent]
):
    """
    Tick context used by all entity tutorial scenes.
    """


class EntityExampleScene(
    GameScene[EntityExampleTickContext, EntityExampleWorld]
):
    """
    Base class for simple entity tutorial scenes.
    """

    tick_context_type = EntityExampleTickContext

    def __init__(self, ctx: RuntimeContext):
        super().__init__(ctx)
        self._texture_ids: list[int] = []

    def on_exit(self) -> None:
        render_backend = getattr(self.context.services.render, "backend", None)
        backend_render = getattr(render_backend, "render", None)
        destroy = getattr(backend_render, "destroy_texture", None)
        if not callable(destroy):
            return
        destroy_texture = cast(Callable[[int], None], destroy)
        for tex_id in self._texture_ids:
            destroy_texture(int(tex_id))  # pylint: disable=not-callable
        self._texture_ids.clear()

    def remember_texture(self, tex_id: int) -> int:
        """
        Track a procedural texture id so the scene can destroy it on exit.
        """
        self._texture_ids.append(int(tex_id))
        return int(tex_id)


@dataclass
class WorldClockSystem(BaseSystem[EntityExampleTickContext]):
    """
    Advances shared example time.
    """

    name: str = "entity_example_clock"
    phase: int = SystemPhase.SIMULATION
    order: int = 5

    def step(self, ctx: EntityExampleTickContext) -> None:
        ctx.world.elapsed += ctx.dt
        ctx.world.frame += 1


@dataclass
class ExampleMotionSystem(BaseSystem[EntityExampleTickContext]):
    """
    Moves tagged entities using built-in motion helpers, then adds bounce rules.
    """

    name: str = "entity_example_motion"
    phase: int = SystemPhase.SIMULATION
    order: int = 20
    _motion: KinematicMotionSystem[EntityExampleTickContext] = field(
        init=False,
        repr=False,
    )
    _constraints: ViewportConstraintSystem[EntityExampleTickContext] = field(
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        def _moving_entities(
            ctx: EntityExampleTickContext,
        ) -> tuple[BaseEntity, ...]:
            return tuple(
                entity
                for entity in ctx.world.entities
                if bool(getattr(entity, "example_motion_enabled", False))
            )

        self._motion = KinematicMotionSystem(
            bindings=(MotionBinding(entities_getter=_moving_entities),),
        )
        self._constraints = ViewportConstraintSystem(
            bindings=(
                ViewportConstraintBinding(
                    entities_getter=_moving_entities,
                    policy="clamp",
                ),
            ),
        )

    def step(self, ctx: EntityExampleTickContext) -> None:
        vw, vh = ctx.world.viewport
        self._motion.step(ctx)

        for entity in ctx.world.entities:
            if not bool(getattr(entity, "example_motion_enabled", False)):
                continue
            if entity.kinematic is None:
                continue

            max_x = max(vw - entity.transform.size.width, 0.0)
            max_y = max(vh - entity.transform.size.height, 0.0)
            x = float(entity.transform.center.x)
            y = float(entity.transform.center.y)

            if x <= 0.0 or x >= max_x:
                entity.kinematic.velocity.x *= -1.0
            if y <= 0.0 or y >= max_y:
                entity.kinematic.velocity.y *= -1.0

        # Bounce inversion is example-specific; position clamping is built-in.
        self._constraints.step(ctx)


@dataclass
class ExampleSpinSystem(BaseSystem[EntityExampleTickContext]):
    """
    Rotates entities that expose a ``spin_deg`` attribute.
    """

    name: str = "entity_example_spin"
    phase: int = SystemPhase.SIMULATION
    order: int = 25

    def step(self, ctx: EntityExampleTickContext) -> None:
        for entity in ctx.world.entities:
            spin_deg = float(getattr(entity, "spin_deg", 0.0))
            if abs(spin_deg) <= 0.0001:
                continue
            entity.rotation_deg = (
                entity.rotation_deg + spin_deg * ctx.dt
            ) % 360.0


@dataclass
class ExampleAnimationSystem(BaseSystem[EntityExampleTickContext]):
    """
    Steps any animation component present in the world.
    """

    name: str = "entity_example_anim"
    phase: int = SystemPhase.SIMULATION
    order: int = 15

    def step(self, ctx: EntityExampleTickContext) -> None:
        for entity in ctx.world.entities:
            if entity.anim is None:
                continue
            entity.anim.step(ctx.dt)


class TextPanelOverlay(Drawable[EntityExampleTickContext]):
    """
    Reusable right-side text panel for entity examples.
    """

    def __init__(
        self,
        *,
        title: str,
        lines_factory: Callable[[EntityExampleTickContext], list[str]],
    ):
        self._title = title
        self._lines_factory = lines_factory

    def draw(self, backend, ctx: EntityExampleTickContext) -> None:
        vw, vh = ctx.world.viewport
        panel_w = min(330, max(260, int(vw * 0.34)))
        panel_h = min(int(vh - 48), 300)
        panel_x = int(vw - panel_w - 24)
        panel_y = 24
        lines = [self._title, "", *self._lines_factory(ctx)]
        layout = fit_text_block(
            backend,
            lines,
            max_width=panel_w - 28,
            max_height=panel_h - 28,
            preferred_font_size=18,
            min_font_size=10,
        )
        backend.render.draw_rect(
            panel_x,
            panel_y,
            panel_w,
            panel_h,
            color=(0, 0, 0, 220),
        )
        draw_text_block(
            backend,
            x=panel_x + 14,
            y=panel_y + 14,
            lines=lines,
            layout=layout,
            color=(232, 232, 236),
        )


def build_render_system(
    *,
    title: str,
    lines_factory: Callable[[EntityExampleTickContext], list[str]],
    overlays: Iterable[RenderOverlay[EntityExampleTickContext]] = (),
) -> ConfiguredQueuedRenderSystem[EntityExampleTickContext]:
    """
    Build the standard queued renderer used by entity tutorial scenes.
    """
    return ConfiguredQueuedRenderSystem(
        name=f"{title.lower().replace(' ', '_')}_render",
        overlays=(
            RenderOverlay.from_drawable(
                TextPanelOverlay(title=title, lines_factory=lines_factory),
                layer="ui",
                z=200,
            ),
            *tuple(overlays),
        ),
    )


def entity_from_dict(payload: dict) -> BaseEntity:
    """
    Small alias that keeps tutorial scene code readable.
    """
    return BaseEntity.from_dict(payload)
