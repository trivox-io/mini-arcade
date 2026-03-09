"""
Game and example runner logic.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional

try:
    import tomllib  # pyright: ignore[reportMissingImports] # py311+
except ModuleNotFoundError:  # py39-310
    import tomli as tomllib  # type: ignore

from mini_arcade.cli.base_command_processor import BaseCommandProcessor
from mini_arcade.cli.exceptions import CommandException

# ------------------------- TOML helpers --------------------------------------

INTERRUPTED_EXIT_CODE = 130


class TargetMetadataError(RuntimeError):
    """Raised when there is an error loading target metadata from pyproject.toml."""


def _load_tool_table(project_dir: Path) -> dict[str, Any]:
    pyproject = project_dir / "pyproject.toml"
    if not pyproject.exists():
        raise TargetMetadataError(f"Missing pyproject.toml: {project_dir}")

    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    tool = data.get("tool", {}) if isinstance(data, dict) else {}

    ma = tool.get("mini-arcade") or tool.get("mini_arcade")
    if not isinstance(ma, dict):
        raise TargetMetadataError(
            f"Missing [tool.mini-arcade] (or [tool.mini_arcade]) table in {pyproject}"
        )

    return ma


def load_game_meta(game_dir: Path) -> dict[str, Any]:
    """
    Load game metadata from pyproject.toml. The pyproject.toml must contain a
    [tool.mini-arcade.game] table with at least the following fields:

    - id (optional): The game id (defaults to the folder name if not provided).
    - entrypoint (optional): The relative path to the game's entrypoint script
        (defaults to "manage.py" if not provided).

    :param game_dir: The directory of the game to load metadata from.
    :type game_dir: Path
    :return: The game metadata as a dictionary.
    :rtype: dict[str, Any]
    :raises TargetMetadataError: If the pyproject.toml is missing or does not contain
        the required table.
    """
    ma = _load_tool_table(game_dir)
    game = ma.get("game")
    if not isinstance(game, dict):
        raise TargetMetadataError(
            f"Missing [tool.mini-arcade.game] in {game_dir / 'pyproject.toml'}"
        )
    return game


# NOTE: examples are CODE-DRIVEN now; no pyproject required.
# We keep this function for backwards compatibility if you *want*
# to support pyproject-based examples later.
def load_example_meta(example_dir: Path) -> dict[str, Any]:
    """
    Load example metadata from pyproject.toml, if present. This is optional for examples,
        but if provided, it must contain a [tool.mini-arcade.example] table.

    :param example_dir: The directory of the example to load metadata from.
    :type example_dir: Path
    :return: The example metadata as a dictionary.
    :rtype: dict[str, Any]
    :raises TargetMetadataError: If the pyproject.toml is missing or does not
        contain the required table.
    """
    ma = _load_tool_table(example_dir)
    ex = ma.get("example")
    if not isinstance(ex, dict):
        raise TargetMetadataError(
            f"Missing [tool.mini-arcade.example] in {example_dir / 'pyproject.toml'}"
        )
    return ex


# ------------------------- Spec + PYTHONPATH ---------------------------------


@dataclass(frozen=True)
class TargetSpec:
    """
    Specification for a target (game or example) to run.

    :ivar kind: str: The kind of target ("game" or "example").
    :ivar target_id: str: The id of the target (e.g. game id or example id).
    :ivar root_dir: Path: The root directory of the target.
    :ivar entrypoint: Path: The path to the entrypoint script to execute.
    :ivar meta: dict[str, Any]: The metadata loaded from pyproject.toml (for games)
        or inferred (for examples).
    """

    kind: str  # "game" | "example"
    target_id: str
    root_dir: Path
    entrypoint: Path
    meta: dict[str, Any]


def _build_pythonpath(spec: TargetSpec) -> str:
    """
    Build PYTHONPATH for a target.

    - games: uses spec.root_dir / source_roots (defaults to ["src"])
    - examples: adds repo_root + repo_root/examples so imports like
      `examples._shared.runner` work from any example folder.
    """
    roots = spec.meta.get("source_roots") or ["src"]
    if not isinstance(roots, list) or not all(
        isinstance(x, str) for x in roots
    ):
        roots = ["src"]

    abs_roots = [(spec.root_dir / r).resolve() for r in roots]
    abs_roots = [p for p in abs_roots if p.exists() and p.is_dir()]

    # Special handling for examples: ensure repo-root import works
    if spec.kind == "example":
        repo_root = spec.root_dir.parent  # examples/<example_id> -> examples/
        # If examples are nested deeper, keep climbing until we find `examples/`
        # (safe guard)
        if repo_root.name != "examples":
            p = spec.root_dir
            for _ in range(5):
                p = p.parent
                if p.name == "examples":
                    repo_root = p
                    break
            # repo_root is now ".../examples"
        project_root = (
            repo_root.parent
        )  # ".../<repo>/examples" -> ".../<repo>"
        abs_roots = [
            project_root.resolve(),  # allow `import examples...`
            repo_root.resolve(),  # allow `import _shared...` if ever needed
            *abs_roots,  # allow example-local src/
        ]

    existing = (os.environ.get("PYTHONPATH") or "").strip()
    parts = [str(p) for p in abs_roots]
    if existing:
        parts.append(existing)

    return os.pathsep.join(parts)


def _stop_process(proc: subprocess.Popen) -> None:
    """
    Try to stop a subprocess gracefully, then force-kill if needed.
    """
    if proc.poll() is not None:
        return

    proc.terminate()
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=3)


def _run_child_process(
    *,
    cmd: list[str],
    cwd: Path,
    env: dict[str, str],
) -> tuple[int, bool]:
    """
    Run one subprocess and handle Ctrl+C interruption.

    :return: (exit_code, interrupted)
    """
    proc = subprocess.Popen(
        cmd,
        cwd=str(cwd),
        env=env,
    )

    try:
        while True:
            code = proc.poll()
            if code is not None:
                return int(code or 0), False
            time.sleep(0.1)
    except KeyboardInterrupt:
        _stop_process(proc)
        return INTERRUPTED_EXIT_CODE, True


# ------------------------- Locators ------------------------------------------


class BaseTargetLocator:
    """
    Base class for locating a target (game or example) based on command arguments.

    :cvar kind: str: The kind of target this locator handles (e.g. "game" or "example").
            Used in error messages and TargetSpec.
    """

    kind: str = "target"

    def __init__(self, *, dev_default_parent_dir: Path):
        self._dev_default_parent_dir = dev_default_parent_dir

    def resolve_parent_dir(self, parent_override: Optional[str]) -> Path:
        """
        Resolve the parent directory for the target, using the override if provided,
        or falling back to the dev default.

        :param parent_override: An optional string path to override the default parent directory.
        :type parent_override: Optional[str]
        :return: The resolved parent directory as a Path object.
        :rtype: Path
        :raises CommandException: If the provided override path does not exist
            or is not a directory.
        """
        if parent_override:
            p = Path(parent_override).expanduser().resolve()
            if not p.exists() or not p.is_dir():
                raise CommandException(
                    f"--{self.kind}s-dir is not a directory: {p}"
                )
            return p
        return self._dev_default_parent_dir

    def find_dir(self, parent_dir: Path, target_id: str) -> Path:
        """
        Find the target directory under the parent directory.

        :param parent_dir: The parent directory to search under.
        :type parent_dir: Path
        :param target_id: The id/folder name of the target to find.
        :type target_id: str
        :return: The resolved path to the target directory.
        :rtype: Path
        :raises CommandException: If the target directory does not exist or is not a directory.
        """
        target_dir = (parent_dir / target_id).resolve()
        if not target_dir.exists() or not target_dir.is_dir():
            raise CommandException(
                f"{self.kind.capitalize()} '{target_id}' not found under: {parent_dir}"
            )
        return target_dir

    def validate(self, target_dir: Path) -> TargetSpec:
        """
        Validate the target directory and return a TargetSpec.

        :param target_dir: The directory of the target to validate.
        :type target_dir: Path
        :return: A TargetSpec instance with the validated target information.
        :rtype: TargetSpec
        """
        raise NotImplementedError


class GameLocator(BaseTargetLocator):
    """
    Game locator with TOML-DRIVEN validation. See validate() for the signature.

    :cvar kind: str: The kind of target this locator handles (e.g. "game" or "example").
        Used in error messages and TargetSpec.
    """

    kind = "game"

    def validate(self, target_dir: Path) -> TargetSpec:
        try:
            meta = load_game_meta(target_dir)
        except TargetMetadataError as e:
            raise CommandException(f"Not a Mini Arcade game: {e}") from e

        meta_id = meta.get("id")
        target_id = (
            str(meta_id).strip()
            if isinstance(meta_id, str) and meta_id.strip()
            else target_dir.name
        )

        entry_rel = meta.get("entrypoint", "manage.py")
        if not isinstance(entry_rel, str) or not entry_rel.strip():
            raise CommandException(
                f"Invalid [tool.mini-arcade.game].entrypoint in {target_dir / 'pyproject.toml'}"
            )

        entrypoint = (target_dir / entry_rel).resolve()
        if not entrypoint.exists() or not entrypoint.is_file():
            raise CommandException(
                f"Entrypoint '{entry_rel}' not found for game '{target_id}' in: {target_dir}"
            )

        meta.setdefault("source_roots", ["src"])

        return TargetSpec(
            kind="game",
            target_id=target_id,
            root_dir=target_dir,
            entrypoint=entrypoint,
            meta=meta,
        )


class ExampleLocator(BaseTargetLocator):
    """
    Example locator with CODE-DRIVEN validation. See validate() for the signature.

    :cvar kind: str: The kind of target this locator handles (e.g. "game" or "example").
        Used in error messages and TargetSpec.
    """

    kind = "example"

    def validate(self, target_dir: Path) -> TargetSpec:
        """
        CODE-DRIVEN example validation:

        We do NOT require pyproject.toml.

        Signature for examples:
          - examples/<example_id>/main.py exists
          - OR examples/<example_id>/run_example.py exists
          - Optional: examples/<example_id>/src/ exists (added to PYTHONPATH if present)

        The entrypoint is always the shared runner:
          <repo_root>/examples/_shared/run_example.py

        The example_id is the path under examples root
        (e.g. config/engine_config_basics).
        """
        target_id = target_dir.name

        # detect example module existence (minimal signature)
        has_main = (target_dir / "main.py").exists()
        has_run_file = (target_dir / "run_example.py").exists()
        has_src = (target_dir / "src").exists()

        if not (has_main or has_run_file or has_src):
            raise CommandException(
                f"Not a Mini Arcade example: expected at least one of "
                f"main.py, run_example.py, or src/ under {target_dir}"
            )

        # shared entrypoint
        examples_root = target_dir.parent  # .../examples
        # If nested, try to find real examples root
        if examples_root.name != "examples":
            p = target_dir
            for _ in range(5):
                p = p.parent
                if p.name == "examples":
                    examples_root = p
                    break

        shared_entry = (
            examples_root / "_shared" / "run_example.py"
        ).resolve()
        if not shared_entry.exists():
            raise CommandException(
                f"Shared example runner missing: {shared_entry}"
            )

        # derive canonical id relative to examples root parent folder
        # examples/catalog/config/engine_config_basics -> config/engine_config_basics
        try:
            catalog_root = examples_root / "catalog"
            target_id = str(
                target_dir.resolve().relative_to(catalog_root.resolve())
            ).replace("\\", "/")
        except ValueError:
            target_id = target_dir.name

        meta: dict[str, Any] = {
            "example_id": target_id,
            "source_roots": ["src"],  # used by PYTHONPATH builder
        }

        return TargetSpec(
            kind="example",
            target_id=target_id,
            root_dir=target_dir,
            entrypoint=shared_entry,
            meta=meta,
        )


# ------------------------- Processor -----------------------------------------


# TODO: Refactor this processor in the future to support more commands and shared logic.
# Justification: This class will be refactored in the future to support more commands and
# shared logic, so we allow it to have more attributes for now.
# pylint: disable=too-many-instance-attributes
class GameRunnerProcessor(BaseCommandProcessor):
    """
    Processor for the "run" command, which can run either a game or an example based
    on the provided arguments.

    The processor validates the input arguments, locates the target game or example,
    builds the appropriate PYTHONPATH, and executes the target's entrypoint script
    with any additional passthrough arguments.

    It handles errors gracefully and provides informative messages for common issues
    such as missing targets or entrypoints.
    """

    def __init__(self, **kwargs):
        self.game = kwargs.get("game")
        self.example = kwargs.get("example")

        # games
        self.from_source = kwargs.get("from_source")

        # examples
        self.examples_dir = kwargs.get("examples_dir")

        # both
        self.pass_through = kwargs.get("pass_through", [])
        if not isinstance(self.pass_through, list):
            self.pass_through = [str(self.pass_through)]
        # Accept legacy docs style: --pass-through -- <args...>
        if self.pass_through and self.pass_through[0] == "--":
            self.pass_through = self.pass_through[1:]

        # validate selection
        if bool(self.game) == bool(self.example):  # both set OR both empty
            raise CommandException(
                "Provide exactly one of: --game or --example"
            )

        self._dev_games_dir = (Path.cwd() / "games").resolve()
        self._dev_examples_dir = (Path.cwd() / "examples" / "catalog").resolve()

        self._games = GameLocator(dev_default_parent_dir=self._dev_games_dir)
        self._examples = ExampleLocator(
            dev_default_parent_dir=self._dev_examples_dir
        )

    def run(self):
        if self.game:
            locator = self._games
            parent = locator.resolve_parent_dir(self.from_source)
            target_dir = locator.find_dir(parent, self.game)
            spec = locator.validate(target_dir)

            cmd = [sys.executable, str(spec.entrypoint), *self.pass_through]
            env = os.environ.copy()
            env["PYTHONPATH"] = _build_pythonpath(spec)

        else:
            locator = self._examples
            parent = locator.resolve_parent_dir(self.examples_dir)
            target_dir = locator.find_dir(parent, self.example)
            spec = locator.validate(target_dir)
            requested_example_id = str(self.example).replace("\\", "/").strip("/")

            # IMPORTANT:
            # examples use the shared runner, which needs the example_id.
            # We pass it as argv[1] to run_example.py
            #
            #   python examples/_shared/run_example.py config/engine_config_basics --backend native
            #
            # The shared runner can parse:
            #   sys.argv[1] = example_id
            #   everything after `--` = passthrough to the example builder or scene
            cmd = [
                sys.executable,
                str(spec.entrypoint),
                requested_example_id,
                *self.pass_through,
            ]

            env = os.environ.copy()
            env["PYTHONPATH"] = _build_pythonpath(spec)

        print(f"Running {spec.kind}: {spec.target_id}")
        print(f"cwd={spec.root_dir}")
        print(f"entrypoint={spec.entrypoint}")
        print(f"PYTHONPATH={env['PYTHONPATH']}")
        print(f"cmd={' '.join(cmd)}")

        try:
            exit_code, interrupted = _run_child_process(
                cmd=cmd,
                cwd=spec.root_dir,
                env=env,
            )
            if interrupted:
                print("Interrupted by user.")
            return exit_code
        except FileNotFoundError as e:
            raise CommandException(f"Failed to execute entrypoint: {e}") from e


class ExampleTourBus:
    """
    Lightweight in-process event bus for example tour orchestration.
    """

    def __init__(self):
        self._subscribers: dict[str, list[Callable[..., None]]] = {}

    def on(self, event_type: str, handler: Callable[..., None]):
        self._subscribers.setdefault(event_type, []).append(handler)

    def emit(self, event_type: str, **kwargs):
        for handler in self._subscribers.get(event_type, []):
            handler(**kwargs)


class TourEvents:
    """
    Event names emitted by the examples tour processor.
    """

    SESSION_STARTED = "session_started"
    EXAMPLE_STARTED = "example_started"
    EXAMPLE_FINISHED = "example_finished"
    EXAMPLE_FAILED = "example_failed"
    SESSION_FINISHED = "session_finished"


class ConsoleTourReporter:
    """
    Console reporter subscribed to tour lifecycle events.
    """

    def __init__(self, bus: ExampleTourBus):
        bus.on(TourEvents.SESSION_STARTED, self._on_session_started)
        bus.on(TourEvents.EXAMPLE_STARTED, self._on_example_started)
        bus.on(TourEvents.EXAMPLE_FINISHED, self._on_example_finished)
        bus.on(TourEvents.EXAMPLE_FAILED, self._on_example_failed)
        bus.on(TourEvents.SESSION_FINISHED, self._on_session_finished)

    def _on_session_started(self, *, total: int, examples: list[str]):
        print(f"Starting examples tour ({total} examples).")
        if examples:
            print("Order:")
            for idx, example_id in enumerate(examples, start=1):
                print(f"  {idx}. {example_id}")

    def _on_example_started(
        self,
        *,
        index: int,
        total: int,
        example_id: str,
        cmd: str,
    ):
        print(f"[{index}/{total}] Starting: {example_id}")
        print(f"cmd={cmd}")

    def _on_example_finished(
        self,
        *,
        index: int,
        total: int,
        example_id: str,
        exit_code: int,
    ):
        print(
            f"[{index}/{total}] Finished: {example_id} (exit={exit_code})"
        )

    def _on_example_failed(
        self,
        *,
        index: int,
        total: int,
        example_id: str,
        error: str,
    ):
        print(f"[{index}/{total}] Failed: {example_id} ({error})")

    def _on_session_finished(
        self,
        *,
        total: int,
        passed: int,
        failed: int,
        stopped: bool,
    ):
        status = "stopped early" if stopped else "completed"
        print(
            f"Examples tour {status}: total={total}, passed={passed}, "
            f"failed={failed}"
        )


def _normalize_target_id(raw_value: str) -> str:
    normalized = str(raw_value).replace("\\", "/").strip("/")
    if not normalized:
        raise CommandException("Example id must be non-empty")
    return normalized


def _discover_example_ids(examples_parent: Path) -> list[str]:
    ids: list[str] = []
    base = examples_parent.resolve()

    for main_py in sorted(
        base.rglob("main.py"), key=lambda p: str(p).lower()
    ):
        rel = str(main_py.parent.resolve().relative_to(base))
        rel_id = rel.replace("\\", "/").strip("/")
        if rel_id:
            ids.append(rel_id)

    # preserve order, remove duplicates
    return list(dict.fromkeys(ids))


class ExamplesTourProcessor(BaseCommandProcessor):
    """
    Processor for running examples sequentially in "tour" mode.
    """

    def __init__(self, **kwargs):
        self.examples_dir = kwargs.get("examples_dir")
        self.group = kwargs.get("group")
        self.from_example = kwargs.get("from_example")
        self.to_example = kwargs.get("to_example")
        self.stop_on_fail = bool(kwargs.get("stop_on_fail", False))
        self.list_only = bool(kwargs.get("list_only", False))

        self.pass_through = kwargs.get("pass_through", [])
        if not isinstance(self.pass_through, list):
            self.pass_through = [str(self.pass_through)]
        if self.pass_through and self.pass_through[0] == "--":
            self.pass_through = self.pass_through[1:]

        self._dev_examples_dir = (Path.cwd() / "examples" / "catalog").resolve()
        self._examples = ExampleLocator(
            dev_default_parent_dir=self._dev_examples_dir
        )

    def _resolve_playlist(self, parent_dir: Path) -> list[str]:
        ids = _discover_example_ids(parent_dir)
        ids = [_normalize_target_id(item) for item in ids]

        if self.group:
            group_id = _normalize_target_id(str(self.group))
            prefix = f"{group_id}/"
            ids = [
                example_id
                for example_id in ids
                if example_id == group_id or example_id.startswith(prefix)
            ]

        from_idx = 0
        to_idx = len(ids) - 1

        if self.from_example:
            from_id = _normalize_target_id(str(self.from_example))
            if from_id not in ids:
                raise CommandException(
                    f"--from-example not found in playlist: {from_id}"
                )
            from_idx = ids.index(from_id)

        if self.to_example:
            to_id = _normalize_target_id(str(self.to_example))
            if to_id not in ids:
                raise CommandException(
                    f"--to-example not found in playlist: {to_id}"
                )
            to_idx = ids.index(to_id)

        if ids and from_idx > to_idx:
            raise CommandException(
                "Invalid range: --from-example is after --to-example"
            )

        if not ids:
            return []

        return ids[from_idx : to_idx + 1]

    def _run_one(
        self,
        *,
        parent_dir: Path,
        example_id: str,
        index: int,
        total: int,
        bus: ExampleTourBus,
    ) -> tuple[int, bool]:
        target_dir = self._examples.find_dir(parent_dir, example_id)
        spec = self._examples.validate(target_dir)
        requested_example_id = _normalize_target_id(example_id)

        cmd = [
            sys.executable,
            str(spec.entrypoint),
            requested_example_id,
            *self.pass_through,
        ]
        env = os.environ.copy()
        env["PYTHONPATH"] = _build_pythonpath(spec)

        bus.emit(
            TourEvents.EXAMPLE_STARTED,
            index=index,
            total=total,
            example_id=requested_example_id,
            cmd=" ".join(cmd),
        )

        try:
            exit_code, interrupted = _run_child_process(
                cmd=cmd,
                cwd=spec.root_dir,
                env=env,
            )
        except FileNotFoundError as exc:
            bus.emit(
                TourEvents.EXAMPLE_FAILED,
                index=index,
                total=total,
                example_id=requested_example_id,
                error=str(exc),
            )
            return 1, False
        if interrupted:
            bus.emit(
                TourEvents.EXAMPLE_FAILED,
                index=index,
                total=total,
                example_id=requested_example_id,
                error="interrupted by user",
            )
            return exit_code, True

        bus.emit(
            TourEvents.EXAMPLE_FINISHED,
            index=index,
            total=total,
            example_id=requested_example_id,
            exit_code=exit_code,
        )

        if exit_code != 0:
            bus.emit(
                TourEvents.EXAMPLE_FAILED,
                index=index,
                total=total,
                example_id=requested_example_id,
                error=f"exit code {exit_code}",
            )

        return exit_code, False

    def run(self):
        parent_dir = self._examples.resolve_parent_dir(self.examples_dir)
        playlist = self._resolve_playlist(parent_dir)

        if not playlist:
            raise CommandException(
                f"No runnable examples found under: {parent_dir}"
            )

        if self.list_only:
            for idx, example_id in enumerate(playlist, start=1):
                print(f"{idx}. {example_id}")
            return 0

        bus = ExampleTourBus()
        ConsoleTourReporter(bus)

        total = len(playlist)
        passed = 0
        failed = 0
        stopped = False
        last_error_code = 0

        bus.emit(
            TourEvents.SESSION_STARTED,
            total=total,
            examples=playlist,
        )

        for index, example_id in enumerate(playlist, start=1):
            exit_code, interrupted = self._run_one(
                parent_dir=parent_dir,
                example_id=example_id,
                index=index,
                total=total,
                bus=bus,
            )

            if interrupted:
                failed += 1
                last_error_code = exit_code
                stopped = True
                break

            if exit_code == 0:
                passed += 1
            else:
                failed += 1
                last_error_code = exit_code
                if self.stop_on_fail:
                    stopped = True
                    break

        bus.emit(
            TourEvents.SESSION_FINISHED,
            total=total,
            passed=passed,
            failed=failed,
            stopped=stopped,
        )

        if failed > 0:
            return last_error_code or 1
        return 0
