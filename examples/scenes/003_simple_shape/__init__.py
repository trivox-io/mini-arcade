# Justification: 00n_<example> is a clear and consistent naming convention for example scenes.
# pylint: disable=invalid-name
"""
Example scene module.
"""

from __future__ import annotations

# Importing this package should register scenes if you use auto-register decorators.
# Keep it explicit: import modules that register scenes.
from .main import *  # noqa: F401,F403
