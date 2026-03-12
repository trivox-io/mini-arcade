"""
Reusable procedural particle systems for simple fire/smoke style effects.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Callable, Generic, Iterable, TypeVar, Union

from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.scenes.systems import SystemBundle
from mini_arcade_core.scenes.systems.phases import SystemPhase

# pylint: disable=invalid-name
TCtx = TypeVar("TCtx")
Color = Union[tuple[int, int, int], tuple[int, int, int, int]]
ColorStop = tuple[float, Color]
AlphaStop = tuple[float, int]
# pylint: enable=invalid-name

FIRE_COLOR_RAMP: tuple[ColorStop, ...] = (
    (0.0, (255, 252, 220)),
    (0.14, (255, 236, 150)),
    (0.34, (255, 182, 84)),
    (0.58, (255, 96, 44)),
    (0.82, (172, 36, 18)),
    (1.0, (34, 8, 8)),
)

SMOKE_COLOR_RAMP: tuple[ColorStop, ...] = (
    (0.0, (146, 128, 124)),
    (0.3, (118, 104, 102)),
    (0.7, (82, 76, 78)),
    (1.0, (36, 32, 36)),
)

FIRE_ALPHA_RAMP: tuple[AlphaStop, ...] = (
    (0.0, 48),
    (0.08, 128),
    (0.28, 216),
    (0.72, 138),
    (1.0, 0),
)

SMOKE_ALPHA_RAMP: tuple[AlphaStop, ...] = (
    (0.0, 18),
    (0.18, 42),
    (0.45, 64),
    (0.82, 34),
    (1.0, 0),
)

MAGIC_COLOR_RAMP: tuple[ColorStop, ...] = (
    (0.0, (244, 222, 255)),
    (0.25, (188, 126, 255)),
    (0.55, (108, 72, 255)),
    (0.82, (56, 34, 162)),
    (1.0, (18, 12, 52)),
)

MAGIC_ALPHA_RAMP: tuple[AlphaStop, ...] = (
    (0.0, 34),
    (0.1, 96),
    (0.45, 188),
    (0.82, 92),
    (1.0, 0),
)

POTION_COLOR_RAMP: tuple[ColorStop, ...] = (
    (0.0, (198, 255, 226)),
    (0.28, (120, 255, 200)),
    (0.56, (62, 214, 166)),
    (0.82, (20, 98, 88)),
    (1.0, (8, 36, 34)),
)

POTION_ALPHA_RAMP: tuple[AlphaStop, ...] = (
    (0.0, 22),
    (0.12, 74),
    (0.38, 146),
    (0.84, 60),
    (1.0, 0),
)


def _default_enabled_when(_ctx: object) -> bool:
    return True


def _default_intensity(_ctx: object) -> float:
    return 1.0


def _default_wind(_ctx: object) -> float:
    return 0.0


def _default_viewport(_ctx: object) -> tuple[float, float]:
    return (0.0, 0.0)


@dataclass
class ProceduralParticle:
    """
    One simulated procedural particle.
    """

    x: float
    y: float
    vx: float
    vy: float
    age: float
    lifetime: float
    start_radius: float
    end_radius: float
    phase: float = 0.0


@dataclass
class ProceduralParticleEmitterState:
    """
    Mutable state for one emitter.
    """

    particles: list[ProceduralParticle] = field(default_factory=list)
    spawn_accumulator: float = 0.0
    elapsed: float = 0.0


@dataclass(frozen=True)
class ProceduralParticleBinding(Generic[TCtx]):
    """
    Configuration for one procedural particle emitter.
    """

    state_getter: Callable[[TCtx], ProceduralParticleEmitterState]
    origin_getter: Callable[[TCtx], tuple[float, float]]
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    intensity_getter: Callable[[TCtx], float] = _default_intensity
    wind_getter: Callable[[TCtx], float] = _default_wind
    viewport_getter: Callable[[TCtx], tuple[float, float]] = _default_viewport
    spawn_rate: float = 96.0
    max_particles: int = 180
    spawn_spread_x: float = 18.0
    spawn_spread_y: float = 6.0
    velocity_x: tuple[float, float] = (-20.0, 20.0)
    velocity_y: tuple[float, float] = (-150.0, -70.0)
    acceleration_x: float = 0.0
    acceleration_y: float = -18.0
    turbulence: float = 20.0
    turbulence_frequency: float = 7.0
    drag: float = 0.9
    lifetime: tuple[float, float] = (0.45, 0.9)
    start_radius: tuple[float, float] = (8.0, 14.0)
    end_radius: tuple[float, float] = (1.0, 4.0)
    color_ramp: tuple[ColorStop, ...] = FIRE_COLOR_RAMP
    alpha_ramp: tuple[AlphaStop, ...] = FIRE_ALPHA_RAMP
    render_pass_scales: tuple[float, ...] = (1.4, 0.92, 0.56)
    render_pass_color_scales: tuple[float, ...] = (0.78, 1.0, 1.08)
    render_pass_alpha_scales: tuple[float, ...] = (0.18, 0.52, 0.95)
    intensity_radius_scale: float = 0.45
    intensity_lifetime_scale: float = 0.16
    intensity_velocity_scale: float = 0.28
    seed: int = 1


@dataclass(frozen=True)
class ProceduralParticleProfile:
    """
    Reusable visual/physics preset for a particle emitter style.
    """

    spawn_rate: float
    max_particles: int
    spawn_spread_x: float
    spawn_spread_y: float
    velocity_x: tuple[float, float]
    velocity_y: tuple[float, float]
    acceleration_x: float
    acceleration_y: float
    turbulence: float
    turbulence_frequency: float
    drag: float
    lifetime: tuple[float, float]
    start_radius: tuple[float, float]
    end_radius: tuple[float, float]
    color_ramp: tuple[ColorStop, ...]
    alpha_ramp: tuple[AlphaStop, ...]
    render_pass_scales: tuple[float, ...]
    render_pass_color_scales: tuple[float, ...]
    render_pass_alpha_scales: tuple[float, ...]
    intensity_radius_scale: float = 0.45
    intensity_lifetime_scale: float = 0.16
    intensity_velocity_scale: float = 0.28


FIRE_PARTICLE_PROFILE = ProceduralParticleProfile(
    spawn_rate=138.0,
    max_particles=300,
    spawn_spread_x=28.0,
    spawn_spread_y=10.0,
    velocity_x=(-26.0, 26.0),
    velocity_y=(-188.0, -92.0),
    acceleration_x=0.0,
    acceleration_y=-34.0,
    turbulence=34.0,
    turbulence_frequency=9.4,
    drag=0.9,
    lifetime=(0.46, 1.02),
    start_radius=(12.0, 24.0),
    end_radius=(2.0, 8.0),
    color_ramp=FIRE_COLOR_RAMP,
    alpha_ramp=FIRE_ALPHA_RAMP,
    render_pass_scales=(1.65, 1.0, 0.56),
    render_pass_color_scales=(0.68, 1.0, 1.12),
    render_pass_alpha_scales=(0.14, 0.46, 1.0),
)

SMOKE_PARTICLE_PROFILE = ProceduralParticleProfile(
    spawn_rate=26.0,
    max_particles=90,
    spawn_spread_x=10.0,
    spawn_spread_y=3.0,
    velocity_x=(-10.0, 10.0),
    velocity_y=(-74.0, -34.0),
    acceleration_x=0.0,
    acceleration_y=-6.0,
    turbulence=10.0,
    turbulence_frequency=4.2,
    drag=0.965,
    lifetime=(0.85, 1.55),
    start_radius=(10.0, 18.0),
    end_radius=(18.0, 34.0),
    color_ramp=SMOKE_COLOR_RAMP,
    alpha_ramp=SMOKE_ALPHA_RAMP,
    render_pass_scales=(1.0,),
    render_pass_color_scales=(1.0,),
    render_pass_alpha_scales=(1.0,),
)

MAGIC_PARTICLE_PROFILE = ProceduralParticleProfile(
    spawn_rate=68.0,
    max_particles=160,
    spawn_spread_x=20.0,
    spawn_spread_y=20.0,
    velocity_x=(-42.0, 42.0),
    velocity_y=(-84.0, 40.0),
    acceleration_x=0.0,
    acceleration_y=-8.0,
    turbulence=28.0,
    turbulence_frequency=7.8,
    drag=0.92,
    lifetime=(0.6, 1.2),
    start_radius=(6.0, 14.0),
    end_radius=(1.0, 5.0),
    color_ramp=MAGIC_COLOR_RAMP,
    alpha_ramp=MAGIC_ALPHA_RAMP,
    render_pass_scales=(1.25, 0.82, 0.44),
    render_pass_color_scales=(0.72, 1.0, 1.14),
    render_pass_alpha_scales=(0.16, 0.54, 1.0),
)

POTION_PARTICLE_PROFILE = ProceduralParticleProfile(
    spawn_rate=42.0,
    max_particles=120,
    spawn_spread_x=16.0,
    spawn_spread_y=8.0,
    velocity_x=(-12.0, 12.0),
    velocity_y=(-72.0, -22.0),
    acceleration_x=0.0,
    acceleration_y=-5.0,
    turbulence=12.0,
    turbulence_frequency=4.8,
    drag=0.955,
    lifetime=(0.8, 1.6),
    start_radius=(8.0, 14.0),
    end_radius=(14.0, 26.0),
    color_ramp=POTION_COLOR_RAMP,
    alpha_ramp=POTION_ALPHA_RAMP,
    render_pass_scales=(1.1, 0.66),
    render_pass_color_scales=(0.82, 1.0),
    render_pass_alpha_scales=(0.3, 0.9),
)


def particle_binding_with_profile(
    *,
    profile: ProceduralParticleProfile,
    state_getter: Callable[[TCtx], ProceduralParticleEmitterState],
    origin_getter: Callable[[TCtx], tuple[float, float]],
    intensity_getter: Callable[[TCtx], float] = _default_intensity,
    wind_getter: Callable[[TCtx], float] = _default_wind,
    viewport_getter: Callable[[TCtx], tuple[float, float]] = _default_viewport,
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when,
    seed: int = 1,
) -> ProceduralParticleBinding[TCtx]:
    """
    Build an emitter binding from a reusable particle style profile.
    """

    return ProceduralParticleBinding(
        state_getter=state_getter,
        origin_getter=origin_getter,
        enabled_when=enabled_when,
        intensity_getter=intensity_getter,
        wind_getter=wind_getter,
        viewport_getter=viewport_getter,
        spawn_rate=profile.spawn_rate,
        max_particles=profile.max_particles,
        spawn_spread_x=profile.spawn_spread_x,
        spawn_spread_y=profile.spawn_spread_y,
        velocity_x=profile.velocity_x,
        velocity_y=profile.velocity_y,
        acceleration_x=profile.acceleration_x,
        acceleration_y=profile.acceleration_y,
        turbulence=profile.turbulence,
        turbulence_frequency=profile.turbulence_frequency,
        drag=profile.drag,
        lifetime=profile.lifetime,
        start_radius=profile.start_radius,
        end_radius=profile.end_radius,
        color_ramp=profile.color_ramp,
        alpha_ramp=profile.alpha_ramp,
        render_pass_scales=profile.render_pass_scales,
        render_pass_color_scales=profile.render_pass_color_scales,
        render_pass_alpha_scales=profile.render_pass_alpha_scales,
        intensity_radius_scale=profile.intensity_radius_scale,
        intensity_lifetime_scale=profile.intensity_lifetime_scale,
        intensity_velocity_scale=profile.intensity_velocity_scale,
        seed=seed,
    )


def fire_particle_binding(
    *,
    state_getter: Callable[[TCtx], ProceduralParticleEmitterState],
    origin_getter: Callable[[TCtx], tuple[float, float]],
    intensity_getter: Callable[[TCtx], float] = _default_intensity,
    wind_getter: Callable[[TCtx], float] = _default_wind,
    viewport_getter: Callable[[TCtx], tuple[float, float]] = _default_viewport,
    seed: int = 1,
) -> ProceduralParticleBinding[TCtx]:
    """
    Convenience preset for a warm fire emitter.
    """

    return particle_binding_with_profile(
        profile=FIRE_PARTICLE_PROFILE,
        state_getter=state_getter,
        origin_getter=origin_getter,
        enabled_when=_default_enabled_when,
        intensity_getter=intensity_getter,
        wind_getter=wind_getter,
        viewport_getter=viewport_getter,
        seed=seed,
    )


def smoke_particle_binding(
    *,
    state_getter: Callable[[TCtx], ProceduralParticleEmitterState],
    origin_getter: Callable[[TCtx], tuple[float, float]],
    intensity_getter: Callable[[TCtx], float] = _default_intensity,
    wind_getter: Callable[[TCtx], float] = _default_wind,
    viewport_getter: Callable[[TCtx], tuple[float, float]] = _default_viewport,
    seed: int = 2,
) -> ProceduralParticleBinding[TCtx]:
    """
    Convenience preset for a soft smoke emitter.
    """

    return particle_binding_with_profile(
        profile=SMOKE_PARTICLE_PROFILE,
        state_getter=state_getter,
        origin_getter=origin_getter,
        enabled_when=_default_enabled_when,
        intensity_getter=intensity_getter,
        wind_getter=wind_getter,
        viewport_getter=viewport_getter,
        seed=seed,
    )


def magic_particle_binding(
    *,
    state_getter: Callable[[TCtx], ProceduralParticleEmitterState],
    origin_getter: Callable[[TCtx], tuple[float, float]],
    intensity_getter: Callable[[TCtx], float] = _default_intensity,
    wind_getter: Callable[[TCtx], float] = _default_wind,
    viewport_getter: Callable[[TCtx], tuple[float, float]] = _default_viewport,
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when,
    seed: int = 3,
) -> ProceduralParticleBinding[TCtx]:
    """
    Convenience preset for arcane glow/spark emitters.
    """

    return particle_binding_with_profile(
        profile=MAGIC_PARTICLE_PROFILE,
        state_getter=state_getter,
        origin_getter=origin_getter,
        enabled_when=enabled_when,
        intensity_getter=intensity_getter,
        wind_getter=wind_getter,
        viewport_getter=viewport_getter,
        seed=seed,
    )


def potion_particle_binding(
    *,
    state_getter: Callable[[TCtx], ProceduralParticleEmitterState],
    origin_getter: Callable[[TCtx], tuple[float, float]],
    intensity_getter: Callable[[TCtx], float] = _default_intensity,
    wind_getter: Callable[[TCtx], float] = _default_wind,
    viewport_getter: Callable[[TCtx], tuple[float, float]] = _default_viewport,
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when,
    seed: int = 4,
) -> ProceduralParticleBinding[TCtx]:
    """
    Convenience preset for bubbling potion/fume emitters.
    """

    return particle_binding_with_profile(
        profile=POTION_PARTICLE_PROFILE,
        state_getter=state_getter,
        origin_getter=origin_getter,
        enabled_when=enabled_when,
        intensity_getter=intensity_getter,
        wind_getter=wind_getter,
        viewport_getter=viewport_getter,
        seed=seed,
    )


def _lerp(a: float, b: float, t: float) -> float:
    return a + ((b - a) * t)


def _lerp_color(left: Color, right: Color, t: float) -> Color:
    count = min(len(left), len(right))
    values = tuple(
        int(round(_lerp(float(left[idx]), float(right[idx]), t)))
        for idx in range(count)
    )
    if count == 3:
        return (values[0], values[1], values[2])
    return (values[0], values[1], values[2], values[3])


def _scale_color(color: Color, scalar: float) -> Color:
    rgb = tuple(
        max(0, min(255, int(round(float(channel) * scalar))))
        for channel in color[:3]
    )
    if len(color) == 4:
        return (rgb[0], rgb[1], rgb[2], color[3])
    return (rgb[0], rgb[1], rgb[2])


def _sample_color_ramp(stops: tuple[ColorStop, ...], t: float) -> Color:
    if not stops:
        return (255, 255, 255)

    clamped = max(0.0, min(1.0, float(t)))
    if clamped <= stops[0][0]:
        return stops[0][1]

    for idx in range(1, len(stops)):
        left_pos, left_color = stops[idx - 1]
        right_pos, right_color = stops[idx]
        if clamped <= right_pos:
            span = max(0.0001, float(right_pos - left_pos))
            local_t = (clamped - float(left_pos)) / span
            return _lerp_color(left_color, right_color, local_t)

    return stops[-1][1]


def _sample_alpha_ramp(stops: tuple[AlphaStop, ...], t: float) -> int:
    if not stops:
        return 255

    clamped = max(0.0, min(1.0, float(t)))
    if clamped <= stops[0][0]:
        return int(stops[0][1])

    for idx in range(1, len(stops)):
        left_pos, left_alpha = stops[idx - 1]
        right_pos, right_alpha = stops[idx]
        if clamped <= right_pos:
            span = max(0.0001, float(right_pos - left_pos))
            local_t = (clamped - float(left_pos)) / span
            return int(round(_lerp(float(left_alpha), float(right_alpha), local_t)))

    return int(stops[-1][1])


def _with_alpha(color: Color, alpha: int) -> Color:
    alpha = max(0, min(255, int(alpha)))
    return (int(color[0]), int(color[1]), int(color[2]), alpha)


@dataclass
class ProceduralParticleSimulationSystem(Generic[TCtx]):
    """
    Spawn and simulate particles for one or more emitters.
    """

    name: str = "procedural_particle_simulation"
    phase: int = SystemPhase.SIMULATION
    order: int = 32
    bindings: tuple[ProceduralParticleBinding[TCtx], ...] = ()
    _rngs: tuple[random.Random, ...] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._rngs = tuple(
            random.Random(int(binding.seed)) for binding in self.bindings
        )

    def _spawn_particle(
        self,
        *,
        rng: random.Random,
        binding: ProceduralParticleBinding[TCtx],
        intensity: float,
        origin_x: float,
        origin_y: float,
    ) -> ProceduralParticle:
        intensity_scale = max(0.0, float(intensity))
        extra_intensity = max(0.0, intensity_scale - 1.0)
        radius_scale = 1.0 + (extra_intensity * binding.intensity_radius_scale)
        lifetime_scale = 1.0 + (
            extra_intensity * binding.intensity_lifetime_scale
        )
        velocity_scale = 1.0 + (
            extra_intensity * binding.intensity_velocity_scale
        )
        x = origin_x + rng.uniform(-binding.spawn_spread_x, binding.spawn_spread_x)
        y = origin_y + rng.uniform(-binding.spawn_spread_y, binding.spawn_spread_y)
        vx = rng.uniform(binding.velocity_x[0], binding.velocity_x[1])
        vy = rng.uniform(binding.velocity_y[0], binding.velocity_y[1]) * velocity_scale
        lifetime = rng.uniform(binding.lifetime[0], binding.lifetime[1]) * lifetime_scale
        start_radius = rng.uniform(
            binding.start_radius[0], binding.start_radius[1]
        ) * radius_scale
        end_radius = rng.uniform(binding.end_radius[0], binding.end_radius[1]) * radius_scale
        return ProceduralParticle(
            x=x,
            y=y,
            vx=vx,
            vy=vy,
            age=0.0,
            lifetime=lifetime,
            start_radius=start_radius,
            end_radius=end_radius,
            phase=rng.uniform(0.0, math.tau),
        )

    def step(self, ctx: TCtx) -> None:
        dt = max(0.0, float(getattr(ctx, "dt", 0.0)))
        if dt <= 0.0:
            return

        for binding, rng in zip(self.bindings, self._rngs):
            state = binding.state_getter(ctx)
            state.elapsed += dt

            survivors: list[ProceduralParticle] = []
            wind = float(binding.wind_getter(ctx))
            drag_scale = max(0.0, float(binding.drag)) ** (dt * 60.0)
            for particle in state.particles:
                particle.age += dt
                if particle.age >= particle.lifetime:
                    continue

                wobble = math.sin(
                    (state.elapsed * binding.turbulence_frequency)
                    + particle.phase
                ) * binding.turbulence

                particle.vx += (
                    float(binding.acceleration_x) + wind + wobble
                ) * dt
                particle.vy += float(binding.acceleration_y) * dt
                particle.vx *= drag_scale
                particle.vy *= drag_scale
                particle.x += particle.vx * dt
                particle.y += particle.vy * dt

                vw, vh = binding.viewport_getter(ctx)
                if -64.0 <= particle.x <= (float(vw) + 64.0) and particle.y >= -96.0:
                    survivors.append(particle)

            state.particles = survivors

            if not binding.enabled_when(ctx):
                state.spawn_accumulator = min(state.spawn_accumulator, 1.0)
                continue

            intensity = max(0.0, float(binding.intensity_getter(ctx)))
            available = max(0, int(binding.max_particles) - len(state.particles))
            total = state.spawn_accumulator + (float(binding.spawn_rate) * intensity * dt)
            to_spawn = min(available, int(total))
            state.spawn_accumulator = total - int(total)

            if to_spawn <= 0:
                continue

            origin_x, origin_y = binding.origin_getter(ctx)
            for _ in range(to_spawn):
                state.particles.append(
                    self._spawn_particle(
                        rng=rng,
                        binding=binding,
                        intensity=intensity,
                        origin_x=float(origin_x),
                        origin_y=float(origin_y),
                    )
                )


@dataclass
class ProceduralParticleRenderSystem(Generic[TCtx]):
    """
    Render procedural particles using primitive circles.
    """

    name: str = "procedural_particle_render"
    phase: int = SystemPhase.RENDERING
    order: int = 105
    bindings: tuple[ProceduralParticleBinding[TCtx], ...] = ()

    def step(self, ctx: TCtx) -> None:
        draw_items: list[
            tuple[float, float, float, float, tuple[Color, ...], tuple[float, ...]]
        ] = []

        for binding in self.bindings:
            state = binding.state_getter(ctx)
            for particle in state.particles:
                life_t = max(
                    0.0,
                    min(1.0, particle.age / max(0.0001, particle.lifetime)),
                )
                radius = _lerp(
                    particle.start_radius,
                    particle.end_radius,
                    life_t,
                )
                if radius <= 0.5:
                    continue

                base_color = _sample_color_ramp(binding.color_ramp, life_t)
                base_alpha = _sample_alpha_ramp(binding.alpha_ramp, life_t)
                colors = tuple(
                    _with_alpha(
                        _scale_color(base_color, color_scalar),
                        int(round(base_alpha * alpha_scalar)),
                    )
                    for color_scalar, alpha_scalar in zip(
                        binding.render_pass_color_scales,
                        binding.render_pass_alpha_scales,
                    )
                )
                draw_items.append(
                    (
                        particle.y,
                        particle.x,
                        particle.y,
                        radius,
                        colors,
                        binding.render_pass_scales,
                    )
                )

        snapshot = tuple(sorted(draw_items, key=lambda item: item[0], reverse=True))

        def draw(backend: object) -> None:
            for _, x, y, radius, colors, scales in snapshot:
                for scale, color in zip(scales, colors):
                    draw_radius = max(1, int(round(radius * float(scale))))
                    backend.render.draw_circle(
                        int(round(x)),
                        int(round(y)),
                        draw_radius,
                        color=color,
                    )

        existing_ops = tuple(getattr(getattr(ctx, "packet", None), "ops", ()))
        ctx.packet = RenderPacket.from_ops([*existing_ops, draw])


@dataclass
class ProceduralParticleBundle(SystemBundle[TCtx]):
    """
    Compose simulation and render systems for one or more procedural emitters.
    """

    bindings: tuple[ProceduralParticleBinding[TCtx], ...] = ()
    simulation_name: str = "procedural_particle_simulation"
    simulation_phase: int = SystemPhase.SIMULATION
    simulation_order: int = 32
    render_name: str = "procedural_particle_render"
    render_phase: int = SystemPhase.RENDERING
    render_order: int = 105
    _simulation: ProceduralParticleSimulationSystem[TCtx] = field(
        init=False,
        repr=False,
    )
    _render: ProceduralParticleRenderSystem[TCtx] = field(
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        self._simulation = ProceduralParticleSimulationSystem(
            name=self.simulation_name,
            phase=self.simulation_phase,
            order=self.simulation_order,
            bindings=self.bindings,
        )
        self._render = ProceduralParticleRenderSystem(
            name=self.render_name,
            phase=self.render_phase,
            order=self.render_order,
            bindings=self.bindings,
        )

    def iter_systems(self) -> Iterable[object]:
        return (self._simulation, self._render)


__all__ = [
    "FIRE_COLOR_RAMP",
    "FIRE_PARTICLE_PROFILE",
    "FIRE_ALPHA_RAMP",
    "MAGIC_ALPHA_RAMP",
    "MAGIC_COLOR_RAMP",
    "MAGIC_PARTICLE_PROFILE",
    "POTION_ALPHA_RAMP",
    "POTION_COLOR_RAMP",
    "POTION_PARTICLE_PROFILE",
    "SMOKE_COLOR_RAMP",
    "SMOKE_PARTICLE_PROFILE",
    "SMOKE_ALPHA_RAMP",
    "ProceduralParticle",
    "ProceduralParticleBinding",
    "ProceduralParticleBundle",
    "ProceduralParticleEmitterState",
    "ProceduralParticleProfile",
    "ProceduralParticleRenderSystem",
    "ProceduralParticleSimulationSystem",
    "fire_particle_binding",
    "magic_particle_binding",
    "particle_binding_with_profile",
    "potion_particle_binding",
    "smoke_particle_binding",
]
