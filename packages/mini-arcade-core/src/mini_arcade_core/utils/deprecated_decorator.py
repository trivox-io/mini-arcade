"""
Deprecated utilities for the mini-arcade-core package.
"""

from __future__ import annotations

import functools

from mini_arcade_core.utils.logging import logger


def deprecated(
    reason: str | None = None,
    version: str | None = None,
    alternative: str | None = None,
):
    """
    Mark a function as deprecated.

    :param reason: Optional reason for deprecation
    :type reason: str | None

    :param version: Optional version when it will be removed
    :type version: str | None

    :param alternative: Optional alternative function to use
    :type alternative: str | None
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            message = f"The function {func.__name__} is deprecated"
            if version:
                message += f" and will be removed in version {version}"
            if reason:
                message += f". {reason}"
            if alternative:
                message += f" Use {alternative} instead."
            logger.warning(message)
            return func(*args, **kwargs)

        return wrapper

    return decorator
