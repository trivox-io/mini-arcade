from __future__ import annotations

import math
from dataclasses import dataclass

from mini_arcade_core.engine.render.packet import RenderPacket
from mini_arcade_core.scenes.systems.base_system import BaseSystem
from mini_arcade_core.scenes.systems.phases import SystemPhase

from ..models import GhostState, PlayTickContext


def _mix_color(
    base: tuple[int, int, int],
    accent: tuple[int, int, int],
    amount: float,
) -> tuple[int, int, int]:
    clamped = max(0.0, min(1.0, float(amount)))
    return tuple(
        int((float(b) * (1.0 - clamped)) + (float(a) * clamped))
        for b, a in zip(base, accent)
    )


def _draw_ghost(backend, ctx: PlayTickContext, ghost: GhostState) -> None:
    world = ctx.world
    center_x, center_y = world.layout.cell_center(ghost.navigator.cell)
    radius = max(8, int(world.layout.cell_width * 0.42))

    if ghost.eaten:
        body = (236, 236, 248)
    elif world.frightened.active:
        pulse = 0.5 + (
            0.5
            * math.sin(
                world.ghost_cadence.tick_count
                + world.frightened.remaining_seconds * 9.0
            )
        )
        body = _mix_color((54, 88, 214), (244, 244, 255), pulse * 0.25)
    else:
        body = ghost.color

    backend.render.draw_circle(
        int(center_x),
        int(center_y),
        radius,
        color=body,
    )
    eye_y = int(center_y) - max(2, radius // 5)
    backend.render.draw_circle(
        int(center_x) - max(4, radius // 3),
        eye_y,
        max(2, radius // 4),
        color=(255, 255, 255),
    )
    backend.render.draw_circle(
        int(center_x) + max(4, radius // 3),
        eye_y,
        max(2, radius // 4),
        color=(255, 255, 255),
    )


@dataclass
class PlayRenderSystem(BaseSystem[PlayTickContext]):
    name: str = "play_render"
    phase: int = SystemPhase.RENDERING
    order: int = 100

    def step(self, ctx: PlayTickContext):
        world = ctx.world
        vw, vh = world.viewport
        board_w = world.layout.bounds.cols * world.layout.cell_width
        board_h = world.layout.bounds.rows * world.layout.cell_height

        def draw(backend):
            flash_mix = (
                (world.flash_timer / 0.18) if world.flash_timer > 0.0 else 0.0
            )
            bg = _mix_color((8, 10, 18), world.flash_color, flash_mix * 0.18)
            board_bg = _mix_color(
                (14, 18, 34),
                (26, 36, 82),
                0.28 if world.frightened.active else 0.0,
            )
            backend.render.draw_rect(
                0,
                0,
                int(vw),
                int(vh),
                color=bg,
            )
            backend.render.draw_rect(
                int(world.layout.origin_x) - 8,
                int(world.layout.origin_y) - 8,
                int(board_w) + 16,
                int(board_h) + 16,
                color=(20, 28, 62),
            )
            backend.render.draw_rect(
                int(world.layout.origin_x),
                int(world.layout.origin_y),
                int(board_w),
                int(board_h),
                color=board_bg,
            )

            for coord, tile in world.tile_map.iter_cells():
                if tile != "wall":
                    continue
                x, y, w, h = world.layout.cell_rect(coord)
                backend.render.draw_rect(
                    int(x) + 1,
                    int(y) + 1,
                    int(w) - 2,
                    int(h) - 2,
                    color=(44, 84, 255),
                )
                backend.render.draw_rect(
                    int(x) + 4,
                    int(y) + 4,
                    max(4, int(w) - 8),
                    max(4, int(h) - 8),
                    color=(14, 18, 52),
                )

            pulse = 0.65 + (
                0.35
                * (
                    0.5
                    + 0.5
                    * math.sin(
                        float(world.player_cadence.tick_count)
                        + world.mode_timer.elapsed_in_mode * 6.0
                    )
                )
            )
            for coord, item in world.collectibles.items.items():
                center_x, center_y = world.layout.cell_center(coord)
                if item.kind.value == "power":
                    backend.render.draw_circle(
                        int(center_x),
                        int(center_y),
                        max(5, int(7 * pulse)),
                        color=(255, 214, 74),
                    )
                else:
                    backend.render.draw_circle(
                        int(center_x),
                        int(center_y),
                        3,
                        color=(255, 224, 92),
                    )

            player_x, player_y = world.layout.cell_center(world.player.cell)
            backend.render.draw_circle(
                int(player_x),
                int(player_y),
                max(8, int(world.layout.cell_width * 0.44)),
                color=(255, 228, 52),
            )
            backend.render.draw_circle(
                int(player_x) + 4,
                int(player_y) - 6,
                2,
                color=(24, 24, 24),
            )

            for ghost in world.ghosts:
                _draw_ghost(backend, ctx, ghost)

            backend.text.draw(
                28,
                18,
                f"SCORE {world.score:05d}   BEST {world.best_score:05d}",
                color=(248, 248, 252),
                font_size=22,
            )
            backend.text.draw(
                28,
                int(vh) - 34,
                f"LIVES {world.lives}   PELLETS {world.remaining_collectibles()}   MODE {(world.mode_timer.current_mode or 'scatter').upper()}",
                color=(220, 220, 236),
                font_size=18,
            )

            if world.status_text:
                backend.text.draw(
                    int(vw * 0.5) - 96,
                    int(world.layout.origin_y) - 34,
                    world.status_text,
                    color=(255, 255, 255),
                    font_size=22,
                )

            if world.event_score_text and world.event_score_timer > 0.0:
                ex, ey = world.effect_origin
                backend.text.draw(
                    int(ex) - 12,
                    int(ey) - 28,
                    world.event_score_text,
                    color=(255, 248, 192),
                    font_size=20,
                )

            if world.game_over or world.victory:
                message = (
                    "PRESS SPACE TO RESTART"
                    if world.game_over
                    else "SPACE TO RUN IT AGAIN"
                )
                backend.text.draw(
                    int(vw * 0.5) - 128,
                    int(vh * 0.5) + 26,
                    message,
                    color=(236, 236, 248),
                    font_size=18,
                )

        ctx.packet = RenderPacket.from_ops([draw])
