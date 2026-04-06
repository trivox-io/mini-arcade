"""
System scaffold implementation owned by the system command domain.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from mini_arcade.cli.exceptions import CommandException
from mini_arcade.commands.shared.scaffold import (
    BaseScaffoldProcessor,
    BaseScaffoldSpec,
    render_template_tree,
)

from .models import SystemScaffoldKwargs


def _normalize_system_id(system_id: str) -> str:
    normalized = str(system_id).strip().lower().replace("-", "_")
    if not re.fullmatch(r"[a-z][a-z0-9_]*", normalized):
        raise CommandException(
            "id must start with a letter and use only letters, "
            "numbers, hyphens, or underscores"
        )
    return normalized


def _normalize_case_name(case_name: str) -> str:
    normalized = str(case_name).strip().lower().replace("-", "_")
    if not re.fullmatch(r"[a-z][a-z0-9_]*", normalized):
        raise CommandException(
            "case-name must start with a letter and use only letters, "
            "numbers, hyphens, or underscores"
        )
    return normalized


def _default_title(system_id: str) -> str:
    return system_id.replace("_", " ").title()


def _class_name_from_system_id(system_id: str) -> str:
    return "".join(part.capitalize() for part in system_id.split("_"))


@dataclass(frozen=True)
class SystemScaffoldSpec(BaseScaffoldSpec):
    """
    Specification for generating a minimal system experiment scaffold.
    """

    system_id: str
    case_name: str
    title: str
    class_name: str


class SystemScaffoldProcessor(BaseScaffoldProcessor[SystemScaffoldSpec]):
    """
    Processor for creating minimal reusable system experiments.
    """

    def __init__(self, **kwargs):
        self.kwargs = SystemScaffoldKwargs.from_dict(kwargs)
        self.force = bool(self.kwargs.force)
        self.dry_run = bool(self.kwargs.dry_run)

    def _build_spec(self) -> SystemScaffoldSpec:
        system_id = _normalize_system_id(self.kwargs.id)
        case_name = _normalize_case_name(self.kwargs.case_name or system_id)
        title = (self.kwargs.title or _default_title(system_id)).strip()
        if not title:
            raise CommandException("title must not be empty")

        return SystemScaffoldSpec(
            system_id=system_id,
            case_name=case_name,
            title=title,
            target_dir=(
                Path(self.kwargs.destination).expanduser().resolve()
                / system_id
            ),
            class_name=_class_name_from_system_id(system_id),
        )

    def _template_files(
        self,
        spec: SystemScaffoldSpec,
    ) -> dict[Path, str]:
        return render_template_tree(
            "system",
            spec.target_dir,
            {
                "case_name": spec.case_name,
                "class_name": spec.class_name,
                "system_id": spec.system_id,
                "title": spec.title,
            },
        )

    def _run_help(self, spec: SystemScaffoldSpec) -> str:
        return (
            "Run with: "
            f"python .\\manage.py system --module "
            f"experiments.{spec.system_id}.system_lab_case --visual"
        )

    def _backend_help(self, spec: SystemScaffoldSpec) -> str:
        return (
            "Swap backend with: "
            f"python .\\manage.py system --module "
            f"experiments.{spec.system_id}.system_lab_case --visual "
            "--backend native"
        )

    def _dry_run_messages(self, spec: SystemScaffoldSpec) -> list[str]:
        return [
            self._run_help(spec),
            self._backend_help(spec),
        ]

    def _success_messages(self, spec: SystemScaffoldSpec) -> list[str]:
        return [
            self._run_help(spec),
            self._backend_help(spec),
            f"Or: python .\\experiments\\{spec.system_id}\\manage.py",
        ]

    def _created_message(self, spec: SystemScaffoldSpec) -> str:
        return f"Created system scaffold at {spec.target_dir}"


__all__ = [
    "SystemScaffoldProcessor",
    "SystemScaffoldSpec",
]
