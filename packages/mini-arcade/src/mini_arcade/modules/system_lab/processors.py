"""
Processor for isolated system lab cases.
"""

from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass, field
import json
from typing import Any

from mini_arcade.cli.base_command_processor import BaseCommandProcessor
from mini_arcade.cli.exceptions import CommandException

from .registry import SystemLabRegistry


def _import_case_modules(module_names: list[str]) -> None:
    for module_name in module_names:
        if module_name in sys.modules:
            sys.modules.pop(module_name, None)
        importlib.import_module(module_name)


@dataclass(init=False)
class SystemLabProcessor(BaseCommandProcessor):
    module: list[str] = field(default_factory=list)
    case: str | None = None
    list: bool = False
    steps: int = 1
    json: bool = False
    visual: bool = False

    def __init__(self, **kwargs):
        modules = kwargs.get("module") or []
        self.module = list(modules)
        self.case = kwargs.get("case")
        self.list = bool(kwargs.get("list", False))
        self.steps = int(kwargs.get("steps", 1))
        self.json = bool(kwargs.get("json", False))
        self.visual = bool(kwargs.get("visual", False))

    def _print_case_list(self) -> int:
        names = sorted(SystemLabRegistry.names())
        if self.json:
            print(json.dumps({"cases": names}, indent=2))
            return 0
        for name in names:
            print(name)
        return 0

    def _run_case(self) -> int:
        if self.case is None:
            raise CommandException("Missing --case")
        if not SystemLabRegistry.contains(self.case):
            raise CommandException(f"Unknown system lab case: {self.case}")

        case = SystemLabRegistry.instantiate(self.case)
        if self.visual:
            result = case.run_visual()
            if result is None:
                raise CommandException(
                    f"System lab case does not provide a visual runner: {self.case}"
                )
            return int(result)

        system = case.build_system()
        ctx = case.build_context()

        for step_index in range(int(self.steps)):
            case.before_step(step_index=step_index, system=system, ctx=ctx)
            step = getattr(system, "step", None)
            if not callable(step):
                raise CommandException(
                    f"Registered system object has no callable step(): {system!r}"
                )
            step(ctx)
            case.after_step(step_index=step_index, system=system, ctx=ctx)

        payload: dict[str, Any] = {
            "case": self.case,
            "steps": int(self.steps),
            "system": getattr(system, "name", system.__class__.__name__),
            "context_type": ctx.__class__.__name__,
        }
        payload.update(case.summarize(system=system, ctx=ctx, steps=int(self.steps)))

        if self.json:
            print(json.dumps(payload, indent=2, sort_keys=True, default=str))
        else:
            for key, value in payload.items():
                print(f"{key}: {value}")
        return 0

    def run(self) -> int:
        SystemLabRegistry.clear()
        _import_case_modules(list(self.module))
        if self.list:
            return self._print_case_list()
        return self._run_case()
