"""
System command models aligned with the stable target architecture.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union


SystemKwargsType = Union["SystemKwargs", "SystemScaffoldKwargs"]


@dataclass
class SystemKwargs:
    """
    Keyword arguments for running or listing system cases.
    """

    module: list[str]
    case: str | None
    list: bool
    steps: int
    json: bool
    visual: bool
    backend: str | None

    @staticmethod
    def from_dict(kwargs: dict) -> SystemKwargs:
        modules = kwargs.get("module") or []
        return SystemKwargs(
            module=list(modules),
            case=kwargs.get("case"),
            list=bool(kwargs.get("list", False)),
            steps=int(kwargs.get("steps", 1)),
            json=bool(kwargs.get("json", False)),
            visual=bool(kwargs.get("visual", False)),
            backend=kwargs.get("backend"),
        )


@dataclass
class SystemScaffoldKwargs:
    """
    Keyword arguments for scaffolding a system experiment.
    """

    id: str
    case_name: str | None
    title: str | None
    destination: str
    force: bool
    dry_run: bool

    @staticmethod
    def from_dict(kwargs: dict) -> SystemScaffoldKwargs:
        return SystemScaffoldKwargs(
            id=kwargs["id"],
            case_name=kwargs.get("case_name"),
            title=kwargs.get("title"),
            destination=kwargs.get("destination", "experiments"),
            force=bool(kwargs.get("force", False)),
            dry_run=bool(kwargs.get("dry_run", False)),
        )
