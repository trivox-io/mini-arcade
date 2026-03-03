from __future__ import annotations

from typing import TYPE_CHECKING

from mini_arcade_core.spaces.collision.specs import (
    ColliderSpec,
    RectColliderSpec,
)
from mini_arcade_core.spaces.geometry.transform import Transform2D

if TYPE_CHECKING:
    from mini_arcade_core.engine.entities import BaseEntity


def rect_rect(
    *,
    ax: float,
    ay: float,
    aw: float,
    ah: float,
    bx: float,
    by: float,
    bw: float,
    bh: float,
    inclusive: bool = True,
) -> bool:
    """
    Axis-aligned rectangle intersection.
    """
    a_right = ax + aw
    a_bottom = ay + ah
    b_right = bx + bw
    b_bottom = by + bh

    if inclusive:
        return not (
            a_right < bx or ax > b_right or a_bottom < by or ay > b_bottom
        )

    return not (
        a_right <= bx or ax >= b_right or a_bottom <= by or ay >= b_bottom
    )


def _rect_box(
    collider: RectColliderSpec | None, transform: Transform2D
) -> tuple[float, float, float, float]:
    width = transform.size.width
    height = transform.size.height

    if collider is not None and collider.size is not None:
        width = collider.size.width
        height = collider.size.height

    # Current engine usage treats transform.center as top-left
    return transform.center.x, transform.center.y, width, height


def intersects(
    collider_a: ColliderSpec | None,
    transform_a: Transform2D,
    collider_b: ColliderSpec | None,
    transform_b: Transform2D,
    *,
    inclusive: bool = True,
) -> bool:
    """
    Generic intersection entrypoint.

    Currently implemented:
    - rect vs rect

    Behavior:
    - `None` collider is treated as rect using transform size.
    """
    a_is_rect = collider_a is None or isinstance(collider_a, RectColliderSpec)
    b_is_rect = collider_b is None or isinstance(collider_b, RectColliderSpec)
    if not (a_is_rect and b_is_rect):
        return False

    ax, ay, aw, ah = _rect_box(collider_a, transform_a)
    bx, by, bw, bh = _rect_box(collider_b, transform_b)
    return rect_rect(
        ax=ax,
        ay=ay,
        aw=aw,
        ah=ah,
        bx=bx,
        by=by,
        bw=bw,
        bh=bh,
        inclusive=inclusive,
    )


def intersects_entities(
    a: BaseEntity,
    b: BaseEntity,
    *,
    inclusive: bool = True,
) -> bool:
    """
    Convenience entity-level intersection.
    """
    return intersects(
        a.collider,
        a.transform,
        b.collider,
        b.transform,
        inclusive=inclusive,
    )
