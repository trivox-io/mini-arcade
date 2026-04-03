"""
Canonical example command processors aligned with the target architecture.
"""

from __future__ import annotations

from pathlib import Path

from mini_arcade.cli.base_command_processor import BaseCommandProcessor
from mini_arcade.cli.exceptions import CommandException
from mini_arcade.commands.shared.process import run_child_process
from mini_arcade.commands.shared.process.command_builders import (
    ExampleCommandBuilder,
)
from mini_arcade.commands.shared.process.environment import (
    ExecutionEnvironmentBuilder,
)
from mini_arcade.utils.logging import logger
from mini_arcade.utils.paths import normalize_path

from .examples_tour import (
    ConsoleTourReporter,
    ExampleTourBus,
    ExampleTourContext,
    ExampleTourDiscoverer,
    TourEvents,
)
from .models import ExampleKwargs, ExampleKwargsType, ExampleTourKwargs
from .target_resolver import TargetResolver


class BaseExampleProcessor(BaseCommandProcessor):
    """
    Base processor for example commands, providing shared utilities.
    """

    kwargs: ExampleKwargsType

    def __init__(self):
        self._target_resolver = TargetResolver(self.kwargs)
        self._env_builder = ExecutionEnvironmentBuilder()
        self._command_builder = ExampleCommandBuilder()


class ExampleRunnerProcessor(BaseExampleProcessor):
    """
    Runs one example using the reusable process runner.
    """

    def __init__(self, **kwargs):
        self.kwargs = ExampleKwargs.from_dict(kwargs)
        super().__init__()

    def run(self):
        try:
            logger.debug("Running example...")
            spec = self._target_resolver.resolve()
            logger.debug(f"Resolved example spec: {spec}")
            requested_example_id = normalize_path(self.kwargs.id)
            cmd = self._command_builder.build(
                spec,
                requested_example_id=requested_example_id,
                pass_through=self.kwargs.pass_through,
            )
            env = self._env_builder.build(spec)

            exit_code, interrupted = run_child_process(
                cmd=cmd,
                cwd=spec.root_dir,
                env=env,
            )

            if interrupted:
                logger.warning("Example run was interrupted by user (Ctrl+C).")

            return exit_code
        except ValueError as e:
            raise CommandException(str(e)) from e


class ExamplesTourProcessor(BaseExampleProcessor):
    """
    Runs a sequence of examples using the reusable process runner.
    """

    def __init__(self, **kwargs):
        self.kwargs = ExampleTourKwargs.from_dict(kwargs)
        super().__init__()
        self._discoverer = ExampleTourDiscoverer(
            self._target_resolver.parent_dir
        )

    def _resolve_playlist(self) -> list[str]:
        ids = self._discoverer.discover_example_ids()
        ids = [normalize_path(item) for item in ids]

        if self.kwargs.group:
            group_id = normalize_path(str(self.kwargs.group))
            prefix = f"{group_id}/"
            ids = [
                example_id
                for example_id in ids
                if example_id == group_id or example_id.startswith(prefix)
            ]

        from_idx = 0
        to_idx = len(ids) - 1

        if self.kwargs.from_example:
            from_id = normalize_path(str(self.kwargs.from_example))
            if from_id not in ids:
                raise ValueError(
                    f"--from-example not found in playlist: {from_id}"
                )
            from_idx = ids.index(from_id)

        if self.kwargs.to_example:
            to_id = normalize_path(str(self.kwargs.to_example))
            if to_id not in ids:
                raise ValueError(
                    f"--to-example not found in playlist: {to_id}"
                )
            to_idx = ids.index(to_id)

        if ids and from_idx > to_idx:
            raise ValueError(
                "Invalid range: --from-example is after --to-example"
            )

        if not ids:
            return []

        return ids[from_idx : to_idx + 1]

    def _run_one(
        self,
        context: ExampleTourContext,
        bus: ExampleTourBus,
    ) -> tuple[int, bool]:
        if context.parent_dir is None or context.example_id is None:
            raise ValueError("Examples tour context is incomplete")

        spec = self._target_resolver.resolve_id(context.example_id)
        requested_example_id = normalize_path(context.example_id)
        cmd = self._command_builder.build(
            spec,
            requested_example_id=requested_example_id,
            pass_through=self.kwargs.pass_through,
        )
        env = self._env_builder.build(spec)

        bus.emit(
            TourEvents.EXAMPLE_STARTED,
            index=context.index,
            total=context.total,
            example_id=requested_example_id,
            cmd=" ".join(cmd),
        )

        try:
            exit_code, interrupted = run_child_process(
                cmd=cmd,
                cwd=spec.root_dir,
                env=env,
            )
        except FileNotFoundError as exc:
            bus.emit(
                TourEvents.EXAMPLE_FAILED,
                index=context.index,
                total=context.total,
                example_id=requested_example_id,
                error=str(exc),
            )
            return 1, False

        if interrupted:
            bus.emit(
                TourEvents.EXAMPLE_FAILED,
                index=context.index,
                total=context.total,
                example_id=requested_example_id,
                error="interrupted by user",
            )
            return exit_code, True

        bus.emit(
            TourEvents.EXAMPLE_FINISHED,
            index=context.index,
            total=context.total,
            example_id=requested_example_id,
            exit_code=exit_code,
        )

        if exit_code != 0:
            bus.emit(
                TourEvents.EXAMPLE_FAILED,
                index=context.index,
                total=context.total,
                example_id=requested_example_id,
                error=f"exit code {exit_code}",
            )

        return exit_code, False

    def _list_only(self, playlist: list[str]):
        if self.kwargs.list_only:
            for idx, example_id in enumerate(playlist, start=1):
                print(f"{idx}. {example_id}")
            return True
        return False

    def _tour(self, playlist: list[str], parent_dir: Path) -> int:
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
            context = ExampleTourContext(
                parent_dir=parent_dir,
                example_id=example_id,
                index=index,
                total=total,
            )
            exit_code, interrupted = self._run_one(
                context=context,
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
                if self.kwargs.stop_on_fail:
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

    def run(self):
        try:
            logger.debug("Running examples tour...")
            playlist = self._resolve_playlist()
            parent_dir = self._target_resolver.parent_dir
            if not playlist:
                raise ValueError(
                    f"No runnable examples found under: {parent_dir}"
                )

            if self._list_only(playlist):
                return 0

            return self._tour(playlist, parent_dir)
        except ValueError as e:
            raise CommandException(str(e)) from e


__all__ = [
    "ExampleRunnerProcessor",
    "ExamplesTourProcessor",
]
