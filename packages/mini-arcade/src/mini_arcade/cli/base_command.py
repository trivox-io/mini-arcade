"""
Base command module
This module defines the BaseCommand class, which serves as a base for all
command implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from mini_arcade.cli.base_command_processor import BaseCommandProcessor

from .argument_type import ArgumentType
from .exceptions import CommandException
from .registry import CommandRegistry


class BaseCommand(ABC):
    """
    Base class for all commands.

    Registration is done via the implementation decorator:

        @CommandRegistry.implementation("build")
        class Build(BaseCommand): ...

    or:

        from .command_registry import CommandRegistry
        @CommandRegistry.implementation("build")
        class Build(BaseCommand): ...

    Subclasses should implement the execute(...) method as the main entrypoint.

    :ivar name: Optional[str]: Command name (for registry); defaults to class name lowercased.
    :ivar aliases: Tuple[str, ...]: Optional command aliases.
    :ivar summary: Optional[str]: Short description of the command.
    :ivar epilog: Optional[str]: Additional help text for the command.
    :ivar args: Optional[List[ArgumentType]]: List of command arguments.
    :ivar abstract: bool: If True, the command is not registered (base class
        for shared logic); defaults to False.
    :ivar processor: Optional[BaseCommandProcessor]: The processor associated with this command.
    """

    # Metadata read by CommandRegistry.implementation(...)
    name: Optional[str] = None
    aliases: Tuple[str, ...] = ()
    summary: Optional[str] = None
    epilog: Optional[str] = None
    args: Optional[List[ArgumentType]] = None
    abstract: bool = False  # if True, decorator will skip registration
    processor: Optional[BaseCommandProcessor] = None

    # Keep __init_subclass__ empty to avoid import/registration cycles
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

    @classmethod
    def define_arguments(cls) -> List[ArgumentType]:
        """
        Return the list of ArgumentType for this command.

        :return: List of ArgumentType instances.
        :rtype: List[ArgumentType]
        """
        return list(cls.args or [])

    def validate(self, **_kwargs):
        """Optional argument validation hook."""
        # override in subclasses
        return None

    def set_processor(self, processor: BaseCommandProcessor):
        """
        Set the processor for the command.

        :param processor: The processor for the command.
        :type processor: BaseCommandProcessor
        """
        if not issubclass(processor, BaseCommandProcessor):
            raise CommandException(
                f"Processor {processor} is not a subclass of BaseCommandProcessor"
            )

        self.processor = processor

    def _run(self, **kwargs):
        """Internal run (pre-exec)."""
        if not self.processor:
            raise CommandException("Processor must be set")

        processor_instance: BaseCommandProcessor = self.processor(**kwargs)
        return processor_instance.run()

    @abstractmethod
    def _execute(self, **kwargs):
        """Internal execution step (core logic)."""

    def execute(self, **kwargs):
        """External command entrypoint."""
        return self._execute(**kwargs)


# Bind the implementation_base now that BaseCommand exists (avoids circular import issues)
CommandRegistry.implementation_base = BaseCommand
