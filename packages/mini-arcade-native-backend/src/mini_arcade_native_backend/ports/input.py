"""
Input port implementation for the native backend.
Provides functionality to poll and map input events.
"""

from __future__ import annotations

from mini_arcade_core.backend.events import (  # pyright: ignore[reportMissingImports]
    Event,
)

# Justification: native is a compiled extension module.
# pylint: disable=no-name-in-module
from mini_arcade_native_backend import _native as native  # type: ignore
from mini_arcade_native_backend.mapping.events import NativeEventMapper


class InputPort:
    """
    Input port for the Mini Arcade native backend.

    :param native_backend: The native backend instance.
    :type native_backend: native.Backend
    :param mapper: The event mapper to convert native events to core events.
    :type mapper: NativeEventMapper
    """

    def __init__(
        self, native_backend: native.Backend, mapper: NativeEventMapper
    ):
        self._b = native_backend
        self._mapper = mapper

    def poll(self) -> list[Event]:
        """
        Poll for input events and map them to core events.

        :return: A list of core events.
        :rtype: list[Event]
        """
        return [self._mapper.to_core(ev) for ev in self._b.poll_events()]
