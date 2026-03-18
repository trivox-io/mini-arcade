from __future__ import annotations

from mini_arcade_core.scenes.systems.builtins import (
    MAGIC_PARTICLE_PROFILE,
    ProceduralParticleBundle,
    particle_binding_with_profile,
)

from .systems import PlayRenderSystem, PlayRulesSystem


def build_play_systems() -> tuple[object, ...]:
    return (
        PlayRulesSystem(),
        PlayRenderSystem(),
        ProceduralParticleBundle(
            bindings=(
                particle_binding_with_profile(
                    profile=MAGIC_PARTICLE_PROFILE,
                    state_getter=lambda ctx: ctx.world.particles,
                    origin_getter=lambda ctx: ctx.world.effect_origin,
                    enabled_when=lambda ctx: ctx.world.effect_timer > 0.0,
                    intensity_getter=lambda ctx: max(
                        0.6,
                        float(ctx.world.effect_intensity),
                    ),
                    viewport_getter=lambda ctx: ctx.world.viewport,
                    seed=41,
                ),
            ),
            render_order=108,
        ),
    )
