from __future__ import annotations

from mini_arcade_core.scenes.systems.builtins import (
    CardinalDirection,
    CollectibleKind,
    GridBounds,
    GridCoord,
    GridLayout,
    GridNavigatorState,
    TileMap,
    tile_map_from_strings,
)

from .models import GhostState, PlayWorld

MAZE_ROWS: tuple[str, ...] = (
    "#################",
    "#o....#...#....o#",
    "#.##.#.#.#.#.##.#",
    "#...............#",
    "#.##.#.###.#.##.#",
    "#....#..P..#....#",
    "####.###.###.####",
    "#....#B.I.C#....#",
    "####.#.###.#.####",
    "#....#..K..#....#",
    "#.##.#.###.#.##.#",
    "#...............#",
    "#.##.#.#.#.#.##.#",
    "#o..#...#...#..o#",
    "#.#.###.#.###.#.#",
    "#...............#",
    "#################",
)

GHOST_COLORS = {
    "B": (255, 64, 64),
    "I": (88, 236, 255),
    "C": (255, 178, 56),
    "K": (255, 120, 214),
}

GHOST_SCATTER_TARGETS = {
    "B": GridCoord(col=15, row=1),
    "I": GridCoord(col=15, row=15),
    "C": GridCoord(col=1, row=15),
    "K": GridCoord(col=1, row=1),
}


def _build_tile_map() -> TileMap[str]:
    legend = {"#": "wall"}
    for char in ".oPBIKC":
        legend[char] = "lane"
    return tile_map_from_strings(
        *MAZE_ROWS,
        legend=legend,
        default="wall",
    )


def _build_layout(
    *,
    viewport: tuple[float, float],
    bounds: GridBounds,
) -> GridLayout:
    cell_size = 24.0
    board_w = float(bounds.cols) * cell_size
    board_h = float(bounds.rows) * cell_size
    vw, vh = viewport
    origin_x = (float(vw) - board_w) * 0.5
    origin_y = max(60.0, (float(vh) - board_h) * 0.5)
    return GridLayout(
        bounds=bounds,
        cell_width=cell_size,
        cell_height=cell_size,
        origin_x=origin_x,
        origin_y=origin_y,
    )


def _scan_maze() -> tuple[
    GridCoord,
    tuple[tuple[GridCoord, CollectibleKind], ...],
    list[GhostState],
]:
    player_start = GridCoord(col=8, row=5)
    collectibles: list[tuple[GridCoord, CollectibleKind]] = []
    ghosts: list[GhostState] = []

    for row_idx, row in enumerate(MAZE_ROWS):
        for col_idx, char in enumerate(row):
            coord = GridCoord(col=col_idx, row=row_idx)
            if char == "P":
                player_start = coord
            elif char == ".":
                collectibles.append((coord, CollectibleKind.PELLET))
            elif char == "o":
                collectibles.append((coord, CollectibleKind.POWER))
            elif char in GHOST_COLORS:
                ghosts.append(
                    GhostState(
                        name=char,
                        color=GHOST_COLORS[char],
                        navigator=GridNavigatorState(
                            cell=coord,
                            direction=CardinalDirection.LEFT,
                        ),
                        spawn_cell=coord,
                        start_direction=CardinalDirection.LEFT,
                        scatter_target=GHOST_SCATTER_TARGETS[char],
                    )
                )

    return player_start, tuple(collectibles), ghosts


def build_play_world(*, viewport: tuple[float, float]) -> PlayWorld:
    tile_map = _build_tile_map()
    layout = _build_layout(viewport=viewport, bounds=tile_map.bounds)
    player_start, collectible_blueprint, ghosts = _scan_maze()

    world = PlayWorld(
        entities=[],
        viewport=viewport,
        layout=layout,
        tile_map=tile_map,
        player=GridNavigatorState(
            cell=player_start,
            direction=CardinalDirection.LEFT,
        ),
        player_start=player_start,
        player_start_direction=CardinalDirection.LEFT,
        ghosts=ghosts,
        collectible_blueprint=collectible_blueprint,
        status_text="READY!",
        status_timer=1.0,
    )
    world.reset_collectibles()
    world.reset_positions()
    return world
