"""
Helpers for building entities from data-driven scene config.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


def deep_merge_dict(
    base: dict[str, Any], overrides: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Deep-merge nested dictionaries, replacing non-dict leaves.
    """
    result = deepcopy(base)
    if not isinstance(overrides, dict):
        return result

    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge_dict(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def resolve_size_value(raw_value: Any, *, axis_size: float) -> float:
    """
    Resolve one size component from config.
    """
    if isinstance(raw_value, (int, float)):
        return float(raw_value)
    if not isinstance(raw_value, dict):
        return 0.0
    if "value" in raw_value:
        return _as_float(raw_value.get("value"))
    if "relative" in raw_value:
        return axis_size * _as_float(raw_value.get("relative"))
    return 0.0


# pylint: disable=too-many-return-statements
def resolve_axis_value(
    raw_value: Any,
    *,
    axis_size: float,
    entity_size: float,
    axis_name: str,
) -> float:
    """
    Resolve one axis position from a config value.

    Supported forms:
    - `12`
    - `{ value: 12 }`
    - `{ anchor: left|center|right, offset: 20 }`
    - `{ anchor: top|middle|bottom, offset: 20 }`
    - `{ relative: 0.5, offset: 0 }`
    """
    if isinstance(raw_value, (int, float)):
        return float(raw_value)
    if not isinstance(raw_value, dict):
        return 0.0

    offset = _as_float(raw_value.get("offset", 0.0))
    if "value" in raw_value:
        return _as_float(raw_value.get("value")) + offset

    if "relative" in raw_value:
        relative = _as_float(raw_value.get("relative"))
        return ((axis_size - entity_size) * relative) + offset

    anchor = str(raw_value.get("anchor", "")).strip().lower()
    if axis_name == "x":
        if anchor in ("left", "start"):
            return offset
        if anchor in ("center", "middle"):
            return ((axis_size - entity_size) * 0.5) + offset
        if anchor in ("right", "end"):
            return (axis_size - entity_size) - offset
    else:
        if anchor in ("top", "start"):
            return offset
        if anchor in ("center", "middle"):
            return ((axis_size - entity_size) * 0.5) + offset
        if anchor in ("bottom", "end"):
            return (axis_size - entity_size) - offset

    return offset


def resolve_transform_layout(
    transform: dict[str, Any] | None,
    *,
    viewport: tuple[float, float],
) -> dict[str, Any]:
    """
    Resolve viewport-relative transform values into plain numeric center coordinates.
    """
    resolved = deepcopy(transform or {})
    size = resolved.get("size", {}) or {}
    viewport_w, viewport_h = viewport
    entity_w = resolve_size_value(size.get("width", 0.0), axis_size=viewport_w)
    entity_h = resolve_size_value(size.get("height", 0.0), axis_size=viewport_h)
    resolved["size"] = {
        "width": entity_w,
        "height": entity_h,
    }

    raw_position = resolved.pop("position", None)
    raw_center = resolved.get("center", {}) or {}
    if isinstance(raw_position, dict):
        raw_center = raw_position

    resolved["center"] = {
        "x": resolve_axis_value(
            raw_center.get("x", 0.0),
            axis_size=viewport_w,
            entity_size=entity_w,
            axis_name="x",
        ),
        "y": resolve_axis_value(
            raw_center.get("y", 0.0),
            axis_size=viewport_h,
            entity_size=entity_h,
            axis_name="y",
        ),
    }
    return resolved


def build_entity_payload(
    template: dict[str, Any],
    *,
    viewport: tuple[float, float],
    overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Merge a template with overrides and resolve transform layout.
    """
    payload = deep_merge_dict(template, overrides)
    payload["transform"] = resolve_transform_layout(
        payload.get("transform"),
        viewport=viewport,
    )
    return payload
