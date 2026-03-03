"""
Collision space utilities.
"""

from __future__ import annotations

from .intersections import intersects, intersects_entities, rect_rect
from .specs import (
    CircleColliderSpec,
    ColliderKind,
    ColliderSpec,
    LineColliderSpec,
    PolyColliderSpec,
    RectColliderSpec,
)

__all__ = [
    "ColliderKind",
    "ColliderSpec",
    "RectColliderSpec",
    "CircleColliderSpec",
    "LineColliderSpec",
    "PolyColliderSpec",
    "rect_rect",
    "intersects",
    "intersects_entities",
]
