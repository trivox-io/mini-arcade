"""
Reusable scaffold processor primitives for command domains.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Generic, Iterator, Mapping, TypeVar

from jinja2 import Environment, StrictUndefined

from mini_arcade.cli.base_command_processor import BaseCommandProcessor
from mini_arcade.cli.exceptions import CommandException

ScaffoldSpecT = TypeVar("ScaffoldSpecT", bound="BaseScaffoldSpec")

_TEMPLATE_ENV = Environment(
    autoescape=False,
    keep_trailing_newline=True,
    undefined=StrictUndefined,
)


@dataclass(frozen=True)
class BaseScaffoldSpec:
    """
    Minimal scaffold spec shared by file-based scaffold processors.
    """

    target_dir: Path


def _iter_template_files(
    root,
    relative_parts: tuple[str, ...] = (),
) -> Iterator[tuple[tuple[str, ...], object]]:
    for child in sorted(root.iterdir(), key=lambda entry: entry.name):
        if child.name == "__pycache__":
            continue
        child_parts = (*relative_parts, child.name)
        if child.is_dir():
            yield from _iter_template_files(child, child_parts)
            continue
        if child.name.endswith((".pyc", ".pyo")):
            continue
        yield child_parts, child


def _render_template_path(
    relative_parts: tuple[str, ...],
    context: Mapping[str, object],
) -> tuple[str, ...]:
    rendered_parts = []
    for part in relative_parts:
        rendered = _TEMPLATE_ENV.from_string(part).render(**context)
        if part.endswith(".jinja"):
            rendered = rendered[: -len(".jinja")]
        rendered_parts.append(rendered)
    return tuple(rendered_parts)


def render_template_tree(
    template_name: str,
    target_dir: Path,
    context: Mapping[str, object],
) -> dict[Path, str]:
    """
    Render one scaffold template tree into a target file map.
    """
    template_root = resources.files("mini_arcade.templates").joinpath(
        template_name
    )
    if not template_root.is_dir():
        raise CommandException(
            f"Template directory not found: mini_arcade.templates/{template_name}"
        )

    files: dict[Path, str] = {}
    for relative_parts, template_file in _iter_template_files(template_root):
        if relative_parts == ("__init__.py",):
            continue

        output_parts = _render_template_path(relative_parts, context)
        content = template_file.read_text(encoding="utf-8")
        if template_file.name.endswith(".jinja"):
            content = _TEMPLATE_ENV.from_string(content).render(**context)
        files[target_dir.joinpath(*output_parts)] = content
    return files


class BaseScaffoldProcessor(
    BaseCommandProcessor,
    Generic[ScaffoldSpecT],
    ABC,
):
    """
    Shared lifecycle for scaffold processors that generate files on disk.
    """

    force: bool
    dry_run: bool

    @abstractmethod
    def _build_spec(self) -> ScaffoldSpecT:
        """
        Build the domain-specific scaffold spec.
        """

    @abstractmethod
    def _template_files(self, spec: ScaffoldSpecT) -> dict[Path, str]:
        """
        Build the file map to write for the scaffold.
        """

    def _dry_run_messages(self, spec: ScaffoldSpecT) -> list[str]:
        """
        Additional messages printed during dry-run mode.
        """

        del spec
        return []

    def _success_messages(self, spec: ScaffoldSpecT) -> list[str]:
        """
        Additional messages printed after a successful scaffold.
        """

        del spec
        return []

    def _target_exists_error(self, spec: ScaffoldSpecT) -> str:
        return f"Target directory already exists: {spec.target_dir}"

    def _created_message(self, spec: ScaffoldSpecT) -> str:
        return f"Created scaffold at {spec.target_dir}"

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
        files = self._template_files(spec)

        if spec.target_dir.exists() and not self.force and not self.dry_run:
            raise CommandException(self._target_exists_error(spec))

        if self.dry_run:
            print(f"Scaffold target: {spec.target_dir}")
            for path in sorted(files):
                print(path.relative_to(spec.target_dir.parent))
            for line in self._dry_run_messages(spec):
                print(line)
            return 0

        spec.target_dir.mkdir(parents=True, exist_ok=True)
        self._write_files(files, force=self.force)
        print(self._created_message(spec))
        for line in self._success_messages(spec):
            print(line)
        return 0


__all__ = [
    "BaseScaffoldProcessor",
    "BaseScaffoldSpec",
    "render_template_tree",
]
