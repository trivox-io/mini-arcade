"""
Processor for isolated system lab cases.
"""

from __future__ import annotations

import importlib
import json
import sys
from dataclasses import dataclass, field
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
    """
    Command processor for running isolated system lab cases.

    :ivar module (list[str]): List of registry module names to import before listing or
        running cases.
    :ivar case (str | None): Registered system lab case name to execute. If not provided,
        the processor will attempt to infer the case to run based on the number of registered
        cases (e.g. if exactly one case is registered, it will be run).
    :ivar list (bool): Whether to list registered cases and exit instead of running a case.
    :ivar steps (int): How many times to call system.step(ctx) when running a case (default is 1).
    :ivar json (bool): Whether to emit machine-readable JSON summary output instead of
        human-readable text.
    :ivar visual (bool): Whether to launch the case's interactive visual runner instead of
        stepping it headlessly.
    """

    module: list[str] = field(default_factory=list)
    case: str | None = None
    list: bool = False
    steps: int = 1
    json: bool = False
    visual: bool = False
    backend: str | None = None

    def __init__(self, **kwargs):
        modules = kwargs.get("module") or []
        self.module = list(modules)
        self.case = kwargs.get("case")
        self.list = bool(kwargs.get("list", False))
        self.steps = int(kwargs.get("steps", 1))
        self.json = bool(kwargs.get("json", False))
        self.visual = bool(kwargs.get("visual", False))
        self.backend = kwargs.get("backend")

    def _print_case_list(self) -> int:
        names = sorted(SystemLabRegistry.names())
        if self.json:
            print(json.dumps({"cases": names}, indent=2))
            return 0
        for name in names:
            print(name)
        return 0

    def _resolve_case_name(self) -> str:
        if self.case is not None:
            return self.case

        names = sorted(SystemLabRegistry.names())
        if self.visual and len(names) == 1:
            return names[0]

        if self.visual and not names:
            raise CommandException("No system lab cases are registered")

        if self.visual:
            joined = ", ".join(names)
            raise CommandException(
                "Missing --case for visual run; available cases: " f"{joined}"
            )

        raise CommandException("Missing --case")

    def _run_case(self) -> int:
        case_name = self._resolve_case_name()
        if not SystemLabRegistry.contains(case_name):
            raise CommandException(f"Unknown system lab case: {case_name}")

        case = SystemLabRegistry.instantiate(case_name)
        if self.visual:
            result = case.run_visual()
            if result is None:
                spec = case.build_visual_spec()
                if spec is None:
                    raise CommandException(
                        "System lab case does not provide a visual runner: "
                        f"{case_name}"
                    )
                # pylint: disable=import-outside-toplevel
                from .visual_runner import run_system_lab_visual_case

                # pylint: enable=import-outside-toplevel

                return run_system_lab_visual_case(
                    case,
                    spec,
                    module_names=tuple(self.module),
                    backend_provider_override=self.backend,
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
            "case": case_name,
            "steps": int(self.steps),
            "system": getattr(system, "name", system.__class__.__name__),
            "context_type": ctx.__class__.__name__,
        }
        payload.update(
            case.summarize(system=system, ctx=ctx, steps=int(self.steps))
        )

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
