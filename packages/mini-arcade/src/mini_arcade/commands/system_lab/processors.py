"""
Processors for isolated system cases.
"""

from __future__ import annotations

import importlib
import json
import sys
from dataclasses import dataclass
from typing import Any

from mini_arcade.cli.base_command_processor import BaseCommandProcessor
from mini_arcade.cli.exceptions import CommandException

from .models import SystemKwargs
from .registry import BaseSystemLabCase, SystemLabRegistry
from .scaffold import SystemScaffoldProcessor


class SystemModuleImporter:
    """
    Imports registry modules so system cases register themselves.
    """

    def import_modules(self, module_names: list[str]) -> None:
        for module_name in module_names:
            if module_name in sys.modules:
                sys.modules.pop(module_name, None)
            importlib.import_module(module_name)


class SystemOutputPresenter:
    """
    Handles human-readable and JSON output for the system domain.
    """

    def print_case_list(self, case_names: list[str], *, json_output: bool) -> int:
        if json_output:
            print(json.dumps({"cases": case_names}, indent=2))
            return 0
        for name in case_names:
            print(name)
        return 0

    def print_summary(
        self,
        payload: dict[str, Any],
        *,
        json_output: bool,
    ) -> int:
        if json_output:
            print(json.dumps(payload, indent=2, sort_keys=True, default=str))
            return 0
        for key, value in payload.items():
            print(f"{key}: {value}")
        return 0


class SystemCaseResolver:
    """
    Resolves which registered system case should be executed.
    """

    def __init__(self, kwargs: SystemKwargs):
        self.kwargs = kwargs

    def resolve_case_name(self) -> str:
        if self.kwargs.case is not None:
            return self.kwargs.case

        names = sorted(SystemLabRegistry.names())
        if self.kwargs.visual and len(names) == 1:
            return names[0]

        if self.kwargs.visual and not names:
            raise CommandException("No system cases are registered")

        if self.kwargs.visual:
            joined = ", ".join(names)
            raise CommandException(
                "Missing --case for visual run; available cases: " f"{joined}"
            )

        raise CommandException("Missing --case")


class SystemCaseExecutor:
    """
    Executes one resolved system case either headlessly or visually.
    """

    def __init__(self, kwargs: SystemKwargs):
        self.kwargs = kwargs

    def _resolve_case(self) -> BaseSystemLabCase:
        case_name = SystemCaseResolver(self.kwargs).resolve_case_name()
        if not SystemLabRegistry.contains(case_name):
            raise CommandException(f"Unknown system case: {case_name}")
        return SystemLabRegistry.instantiate(case_name)

    def _run_visual(self, case: BaseSystemLabCase) -> int:
        result = case.run_visual()
        if result is not None:
            return int(result)

        spec = case.build_visual_spec()
        if spec is None:
            raise CommandException(
                "System case does not provide a visual runner: "
                f"{SystemCaseResolver(self.kwargs).resolve_case_name()}"
            )

        from .visual_runner import run_system_lab_visual_case

        return run_system_lab_visual_case(
            case,
            spec,
            module_names=tuple(self.kwargs.module),
            backend_provider_override=self.kwargs.backend,
        )

    def _run_headless(self, case: BaseSystemLabCase) -> dict[str, Any]:
        case_name = SystemCaseResolver(self.kwargs).resolve_case_name()
        system = case.build_system()
        ctx = case.build_context()

        for step_index in range(int(self.kwargs.steps)):
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
            "steps": int(self.kwargs.steps),
            "system": getattr(system, "name", system.__class__.__name__),
            "context_type": ctx.__class__.__name__,
        }
        payload.update(
            case.summarize(
                system=system,
                ctx=ctx,
                steps=int(self.kwargs.steps),
            )
        )
        return payload

    def execute(self) -> int | dict[str, Any]:
        case = self._resolve_case()
        if self.kwargs.visual:
            return self._run_visual(case)
        return self._run_headless(case)


class BaseSystemProcessor(BaseCommandProcessor):
    """
    Base processor for the system command domain.
    """

    def __init__(self):
        self._module_importer = SystemModuleImporter()
        self._presenter = SystemOutputPresenter()


class SystemRunnerProcessor(BaseSystemProcessor):
    """
    Processor for listing or running isolated system cases.
    """

    def __init__(self, **kwargs):
        self.kwargs = SystemKwargs.from_dict(kwargs)
        super().__init__()
        self._executor = SystemCaseExecutor(self.kwargs)

    def run(self) -> int:
        SystemLabRegistry.clear()
        self._module_importer.import_modules(list(self.kwargs.module))

        if self.kwargs.list:
            return self._presenter.print_case_list(
                sorted(SystemLabRegistry.names()),
                json_output=self.kwargs.json,
            )

        result = self._executor.execute()
        if isinstance(result, int):
            return result
        return self._presenter.print_summary(
            result,
            json_output=self.kwargs.json,
        )


SystemLabProcessor = SystemRunnerProcessor
SystemLabScaffoldProcessor = SystemScaffoldProcessor


__all__ = [
    "BaseSystemProcessor",
    "SystemRunnerProcessor",
    "SystemScaffoldProcessor",
    "SystemLabProcessor",
    "SystemLabScaffoldProcessor",
]
