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


class SystemScaffoldTemplateBuilder:
    """
    Builds the generated file set for a system scaffold.
    """

    def build(self, spec: SystemScaffoldSpec) -> dict[Path, str]:
        """
        Build the file templates for the given system scaffold specification.

        :param spec: The system scaffold specification.
        :type spec: SystemScaffoldSpec
        :return: A mapping of file paths to their generated content.
        :rtype: dict[Path, str]
        """
        project_dir = spec.target_dir
        case_name = spec.case_name
        title = spec.title
        class_name = spec.class_name

        return {
            project_dir
            / "__init__.py": '"""\nGenerated system experiment.\n"""\n',
            project_dir
            / "manage.py": f"""\"\"\"Launch the {title} experiment directly.\"\"\"

from __future__ import annotations

import argparse
from pathlib import Path
import sys


def _find_repo_root(start: Path) -> Path | None:
    for candidate in (start, *start.parents):
        marker = candidate / "packages" / "mini-arcade" / "src"
        if marker.exists():
            return candidate
    return None


def _bootstrap_paths() -> None:
    project_root = Path(__file__).resolve().parent
    repo_root = _find_repo_root(project_root)
    paths = [project_root]

    if repo_root is not None:
        paths.extend(
            [
                repo_root,
                repo_root / "packages" / "mini-arcade" / "src",
                repo_root / "packages" / "mini-arcade-core" / "src",
                repo_root / "packages" / "mini-arcade-pygame-backend" / "src",
                repo_root / "packages" / "mini-arcade-native-backend" / "src",
            ]
        )

    for path in reversed(paths):
        value = str(path)
        if value not in sys.path:
            sys.path.insert(0, value)


_bootstrap_paths()

# Justification: local path bootstrap must run before importing mini_arcade.
# pylint: disable=wrong-import-position
from mini_arcade.commands.system_lab.processors import SystemRunnerProcessor
# pylint: enable=wrong-import-position


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Launch the {title} experiment directly.",
    )
    parser.add_argument(
        "--backend",
        default=None,
        help="Override the visual backend provider (for example: pygame or native).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    raise SystemExit(
        SystemRunnerProcessor(
            module=["system_lab_case"],
            case="{case_name}",
            visual=True,
            backend=args.backend,
        ).run()
    )
""",
            project_dir
            / "system_lab_case.py": f"""\"\"\"Minimal reusable system scaffold for {title}.\"\"\"

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade.commands.system_lab import (
    BaseSystemLabCase,
    SystemLabRegistry,
)
from mini_arcade_core.engine.commands import CommandQueue
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.sim_scene import BaseTickContext, BaseWorld
from mini_arcade_core.scenes.systems.base_system import BaseSystem
from mini_arcade_core.scenes.systems.phases import SystemPhase


@dataclass
class {class_name}World(BaseWorld):
    viewport: tuple[float, float] = (800.0, 600.0)


@dataclass
class {class_name}Context(BaseTickContext[{class_name}World, object]):
    pass


@dataclass
class {class_name}System(BaseSystem[{class_name}Context]):
    name: str = "{case_name}"
    phase: int = SystemPhase.SIMULATION
    order: int = 20

    def step(self, ctx: {class_name}Context) -> None:
        ctx.render_queue.clear()
        ctx.render_queue.text(
            x=24.0,
            y=24.0,
            text="{title}",
            color=(235, 235, 235),
            font_size=20,
        )
        ctx.render_queue.text(
            x=24.0,
            y=52.0,
            text="Replace {class_name}System.step() with your experiment.",
            color=(180, 196, 220),
            font_size=18,
        )
        ctx.render_queue.text(
            x=24.0,
            y=78.0,
            text="F5 reloads this lab after edits.",
            color=(150, 166, 188),
            font_size=16,
        )


@SystemLabRegistry.implementation("{case_name}")
class {class_name}Case(BaseSystemLabCase):
    visual_title = "{title}"
    visual_debug_overlay_title = "{title}"

    def build_system(self) -> object:
        return {class_name}System()

    def build_context(self) -> object:
        return {class_name}Context(
            input_frame=InputFrame(frame_index=0, dt=1.0 / 60.0),
            dt=1.0 / 60.0,
            world={class_name}World(entities=[]),
            commands=CommandQueue(),
        )
""",
        }


class SystemScaffoldProcessor(BaseScaffoldProcessor[SystemScaffoldSpec]):
    """
    Processor for creating minimal reusable system experiments.
    """

    def __init__(self, **kwargs):
        self.kwargs = SystemScaffoldKwargs.from_dict(kwargs)
        self.force = bool(self.kwargs.force)
        self.dry_run = bool(self.kwargs.dry_run)
        self._template_builder = SystemScaffoldTemplateBuilder()

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
        return self._template_builder.build(spec)

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
