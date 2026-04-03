"""
Registry-backed isolated system runner for development.
"""

from .commands import (
    ScaffoldSystemCommand,
    ScaffoldSystemLabCommand,
    SystemCommand,
    SystemLabCommand,
)
from .processors import (
    SystemLabProcessor,
    SystemLabScaffoldProcessor,
    SystemRunnerProcessor,
    SystemScaffoldProcessor,
)
from .registry import BaseSystemLabCase, SystemLabRegistry, SystemLabVisualSpec

__all__ = [
    "SystemCommand",
    "ScaffoldSystemCommand",
    "SystemLabCommand",
    "ScaffoldSystemLabCommand",
    "SystemRunnerProcessor",
    "SystemScaffoldProcessor",
    "SystemLabProcessor",
    "SystemLabScaffoldProcessor",
    "BaseSystemLabCase",
    "SystemLabRegistry",
    "SystemLabVisualSpec",
]
