"""
Runtime environment helpers for command execution.
"""

from __future__ import annotations

import os
from pathlib import Path

from mini_arcade.commands.shared.base_target_locator import TargetSpec


def _find_repo_root(start_dir: Path) -> Path | None:
    """
    Discover the workspace root by walking parents from ``start_dir``.
    """
    start = start_dir.resolve()
    candidates = (start, *start.parents)
    for candidate in candidates:
        packages_dir = candidate / "packages"
        if packages_dir.is_dir() and (candidate / "pyproject.toml").exists():
            return candidate
    return None


def _workspace_source_roots(repo_root: Path | None) -> list[Path]:
    """
    Return package ``src`` roots under the workspace.
    """
    if repo_root is None:
        return []

    packages_dir = repo_root / "packages"
    roots: list[Path] = []
    for package_dir in sorted(packages_dir.iterdir(), key=lambda p: p.name):
        src_dir = package_dir / "src"
        if src_dir.is_dir():
            roots.append(src_dir.resolve())
    return roots


def _build_pythonpath(spec: TargetSpec) -> str:
    """
    Build the effective ``PYTHONPATH`` for a resolved target.
    """
    roots = spec.meta.get("source_roots") or ["src"]
    if not isinstance(roots, list) or not all(
        isinstance(x, str) for x in roots
    ):
        roots = ["src"]

    abs_roots = [(spec.root_dir / r).resolve() for r in roots]
    abs_roots = [p for p in abs_roots if p.exists() and p.is_dir()]
    repo_root = _find_repo_root(spec.root_dir)
    workspace_roots = _workspace_source_roots(repo_root)

    if spec.kind == "example":
        repo_root = spec.root_dir.parent
        if repo_root.name != "examples":
            p = spec.root_dir
            for _ in range(5):
                p = p.parent
                if p.name == "examples":
                    repo_root = p
                    break
        project_root = repo_root.parent
        abs_roots = [
            *workspace_roots,
            project_root.resolve(),
            repo_root.resolve(),
            *abs_roots,
        ]
    elif workspace_roots:
        abs_roots = [*workspace_roots, *abs_roots]

    existing = (os.environ.get("PYTHONPATH") or "").strip()
    parts = [str(p) for p in abs_roots]
    if existing:
        parts.append(existing)

    return os.pathsep.join(parts)


class ExecutionEnvironmentBuilder:
    """
    Builds runtime environment variables for a resolved target.
    """

    def build(self, spec: TargetSpec) -> dict[str, str]:
        """
        Build the environment variables for executing one resolved target.
        """
        env = os.environ.copy()
        env["PYTHONPATH"] = _build_pythonpath(spec)

        settings_path = self._resolve_settings_path(spec)
        if settings_path is not None:
            env["MINI_ARCADE_CONFIG_PATH"] = str(settings_path)

        return env

    def _resolve_settings_path(self, spec: TargetSpec) -> Path | None:
        """
        Resolve the game settings file to inject into the child process env.
        """
        if spec.kind != "game":
            return None

        yml = spec.root_dir / "settings" / "settings.yml"
        yaml = spec.root_dir / "settings" / "settings.yaml"

        if yml.exists():
            return yml.resolve()
        if yaml.exists():
            return yaml.resolve()
        return None
