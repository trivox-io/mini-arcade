"""
Processor for scaffolding minimal reusable system lab experiments.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from mini_arcade.cli.base_command_processor import BaseCommandProcessor
from mini_arcade.cli.exceptions import CommandException


def _normalize_lab_id(lab_id: str) -> str:
    normalized = str(lab_id).strip().lower().replace("-", "_")
    if not re.fullmatch(r"[a-z][a-z0-9_]*", normalized):
        raise CommandException(
            "lab-id must start with a letter and use only letters, "
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


def _default_title(lab_id: str) -> str:
    return lab_id.replace("_", " ").title()


def _class_name_from_lab_id(lab_id: str) -> str:
    return "".join(part.capitalize() for part in lab_id.split("_"))


@dataclass(frozen=True)
class SystemLabScaffoldSpec:
    """
    Specification for generating a minimal system lab scaffold.
    """

    lab_id: str
    case_name: str
    title: str
    target_dir: Path
    class_name: str


def _template_files(spec: SystemLabScaffoldSpec) -> dict[Path, str]:
    project_dir = spec.target_dir
    case_name = spec.case_name
    title = spec.title
    class_name = spec.class_name

    return {
        project_dir / "__init__.py": '"""\nGenerated system lab experiment.\n"""\n',
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
from mini_arcade.modules.system_lab.processors import SystemLabProcessor
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
        SystemLabProcessor(
            module=["system_lab_case"],
            case="{case_name}",
            visual=True,
            backend=args.backend,
        ).run()
    )
""",
        project_dir
        / "system_lab_case.py": f"""\"\"\"Minimal reusable system lab scaffold for {title}.\"\"\"

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade.modules.system_lab import (
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
        # TODO: add your simulation/update logic here.


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


@dataclass(init=False)
class SystemLabScaffoldProcessor(BaseCommandProcessor):
    """
    Processor for creating minimal reusable system lab experiments.
    """

    lab_id: str
    case_name: str | None = None
    title: str | None = None
    destination: str = "experiments"
    force: bool = False
    dry_run: bool = False

    def __init__(self, **kwargs):
        self.lab_id = kwargs.get("lab_id")
        self.case_name = kwargs.get("case_name")
        self.title = kwargs.get("title")
        self.destination = kwargs.get("destination", "experiments")
        self.force = bool(kwargs.get("force", False))
        self.dry_run = bool(kwargs.get("dry_run", False))

    def _build_spec(self) -> SystemLabScaffoldSpec:
        lab_id = _normalize_lab_id(self.lab_id)
        case_name = _normalize_case_name(self.case_name or lab_id)
        title = (self.title or _default_title(lab_id)).strip()
        if not title:
            raise CommandException("title must not be empty")

        return SystemLabScaffoldSpec(
            lab_id=lab_id,
            case_name=case_name,
            title=title,
            target_dir=Path(self.destination).expanduser().resolve() / lab_id,
            class_name=_class_name_from_lab_id(lab_id),
        )

    def _write_files(self, files: dict[Path, str], *, force: bool) -> None:
        for path, content in files.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists() and not force:
                raise CommandException(
                    f"Refusing to overwrite existing file: {path}"
                )
            path.write_text(content, encoding="utf-8")

    def run(self) -> int:
        spec = self._build_spec()
        files = _template_files(spec)

        if spec.target_dir.exists() and not self.force and not self.dry_run:
            raise CommandException(
                f"Target directory already exists: {spec.target_dir}"
            )

        if self.dry_run:
            print(f"Scaffold target: {spec.target_dir}")
            for path in sorted(files):
                print(path.relative_to(spec.target_dir.parent))
            print(
                "Run with: "
                f"python .\\manage.py system-lab --module "
                f"experiments.{spec.lab_id}.system_lab_case --visual"
            )
            print(
                "Swap backend with: "
                f"python .\\manage.py system-lab --module "
                f"experiments.{spec.lab_id}.system_lab_case --visual "
                "--backend native"
            )
            return 0

        spec.target_dir.mkdir(parents=True, exist_ok=True)
        self._write_files(files, force=self.force)
        print(f"Created system lab scaffold at {spec.target_dir}")
        print(
            "Run with: "
            f"python .\\manage.py system-lab --module "
            f"experiments.{spec.lab_id}.system_lab_case --visual"
        )
        print(
            "Swap backend with: "
            f"python .\\manage.py system-lab --module "
            f"experiments.{spec.lab_id}.system_lab_case --visual "
            "--backend native"
        )
        print(f"Or: python .\\experiments\\{spec.lab_id}\\manage.py")
        return 0
