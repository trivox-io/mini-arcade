"""
Shared command-domain primitives.
"""

from .arguments import PassThroughArgument
from .pass_through_normalizer import PassThroughNormalizer
from .scaffold import BaseScaffoldProcessor, BaseScaffoldSpec

__all__ = [
    "BaseScaffoldProcessor",
    "BaseScaffoldSpec",
    "PassThroughArgument",
    "PassThroughNormalizer",
]
