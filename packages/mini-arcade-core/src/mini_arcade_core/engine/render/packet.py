"""
Render packet module.
Defines the RenderPacket class and related types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, Protocol, runtime_checkable

from mini_arcade_core.backend import Backend

DrawOp = Callable[[Backend], None]


@dataclass(frozen=True)
class RenderPacket:
    """
    Minimal render packet for v1.

    It is intentionally backend-agnostic: each op is a callable that knows
    how to draw itself using the Backend instance.

    Later you can replace DrawOp with typed primitives + passes.
    """

    ops: tuple[DrawOp, ...] = ()
    meta: dict[str, object] = field(default_factory=dict)

    @staticmethod
    def from_ops(ops: Iterable[DrawOp], **meta: object) -> "RenderPacket":
        """
        Create a RenderPacket from an iterable of DrawOps and optional meta.

        :param ops: Iterable of DrawOp callables.
        :type ops: Iterable[DrawOp]

        :return: RenderPacket instance.
        :rtype: RenderPacket
        """
        return RenderPacket(ops=tuple(ops), meta=dict(meta))


# TODO: Implement later
@runtime_checkable
class Renderable(Protocol):
    """
    Optional convenience: any object that can produce a RenderPacket.
    """

    def render(self) -> RenderPacket:
        """
        Produce a RenderPacket for this object.

        :return: RenderPacket instance.
        :rtype: RenderPacket
        """
