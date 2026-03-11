"""
Helpers for scene bootstrap/config loading.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable


def scene_entities_config(scene, *, error_message: str) -> dict[str, Any]:
    """
    Return the ``entities`` section from scene runtime settings.
    """
    scene_cfg = scene.scene_runtime_settings()
    entities_cfg = scene_cfg.get("entities", {}) if scene_cfg else {}
    if not isinstance(entities_cfg, dict):
        raise ValueError(error_message)
    return entities_cfg


def resolve_named_templates(
    raw_templates: dict[str, Any] | None,
    *,
    resolver: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> dict[str, dict[str, Any]]:
    """
    Clone and optionally resolve the named template mapping.
    """
    templates = raw_templates or {}
    if resolver is None:
        return {
            str(name): deepcopy(template_data)
            for name, template_data in templates.items()
            if isinstance(template_data, dict)
        }
    return {
        str(name): resolver(template_data)
        for name, template_data in templates.items()
        if isinstance(template_data, dict)
    }


def scene_viewport(scene) -> tuple[float, float]:
    """
    Resolve the current virtual viewport from the window service.
    """
    # Justification: service returns protocol type and static checker
    # does not infer concrete tuple.
    # pylint: disable=assignment-from-no-return
    vw, vh = scene.context.services.window.get_virtual_size()
    # pylint: enable=assignment-from-no-return
    return (float(vw), float(vh))


__all__ = [
    "resolve_named_templates",
    "scene_entities_config",
    "scene_viewport",
]
