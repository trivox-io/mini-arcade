"""
Example entities for 004_shape_gallery.
"""

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade_core.engine.entities import BaseEntity


@dataclass
class MyEntity(BaseEntity):
    """Example entity class."""
