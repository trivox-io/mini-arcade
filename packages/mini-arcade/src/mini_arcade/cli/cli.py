"""
Command line interface for the Mini Arcade application.
"""

from __future__ import annotations

import argparse
import logging
import os
from dataclasses import dataclass
from typing import Any, Iterable, List, Optional, Type

from mini_arcade.cli.argument_type import ArgumentType, coerce_type
from mini_arcade.cli.base_command import BaseCommand
from mini_arcade.cli.exceptions import CommandException
from mini_arcade.cli.registry import CommandRegistry


@dataclass
class CLIConfig:
    """
    Configuration for the CLI application.

    :ivar app_name: Optional[str]: The name of the application.
    :ivar description: Optional[str]: The description of the application.
    :ivar usage: Optional[str]: The usage string for the application.
    :ivar formatter_class: Optional[Type[argparse.HelpFormatter]]:
        The formatter class for the argument parser.
    :ivar parents: Optional[list[argparse.ArgumentParser]]: A list of parent parsers
        to include in the main parser.
    """

    app_name: Optional[str] = None
    description: Optional[str] = None
    usage: Optional[str] = None
    formatter_class: Optional[Type[argparse.HelpFormatter]] = (
        argparse.RawDescriptionHelpFormatter
    )
    parents: Optional[list[argparse.ArgumentParser]] = None


class ParserFactory:
    """
    Factory class to create argument parsers for the CLI application.
    """

    @staticmethod
    def create_main_parser(config: CLIConfig) -> argparse.ArgumentParser:
        """
        Create the main parser for the CLI application.

        :param config: The configuration for the CLI application.
        :type config: CLIConfig

        :return: The main parser for the CLI application.
        :rtype: argparse.ArgumentParser
        """
        p = argparse.ArgumentParser(
            prog=config.app_name,
            description=config.description,
            usage=config.usage,
            formatter_class=config.formatter_class,
            parents=config.parents or [],
        )
        return p


@dataclass
class ArgumentOptions:
    """
    Options for a command line argument.

    :ivar name: str: The name of the argument.
    :ivar aliases: Optional[Iterable[str]]: Optional list of aliases for the argument
        (e.g. ["-v", "--verbose"]).
    :ivar data_type: Type: The data type of the argument.
    :ivar help_text: Optional[str]: The help text for the argument.
    :ivar required: bool: Whether the argument is required.
    :ivar default: Optional[Any]: The default value for the argument.
    :ivar choices: Optional[List[Any]]: The choices for the argument.
    :ivar nargs: Optional[Union[int, str]]: The number of arguments.
    :ivar metavar: Optional[str]: The metavar for the argument.
    :ivar action: Optional[str]: The action for the argument (e.g. "store_true" for flags).
    :ivar version: Optional[str]: The version string for the argument
        (only used when action == "version").
    """

    name: str
    aliases: Optional[Iterable[str]] = None

    # Normal args
    data_type: Any = str
    help_text: str = ""
    required: bool = False
    default: Any = None
    choices: Optional[Iterable[Any]] = None
    nargs: Any = None
    metavar: Optional[str] = None

    # Special flags
    action: Optional[Any] = None
    version: Optional[str] = None  # only used when action == "version"


class ArgumentParserFactory:
    """
    Factory class to create argument to parsers for the CLI application.
    """

    @staticmethod
    def add_argument_parser(
        parser: argparse.ArgumentParser,
        options: ArgumentOptions,
    ) -> argparse.ArgumentParser:
        """
        Add an argument parser for a command.

        :param parser: The main parser for the CLI application.
        :type parser: argparse.ArgumentParser

        :param options: The options for the argument.
        :type options: ArgumentOptions

        :return: The argument parser for the command.
        :rtype: argparse.ArgumentParser
        """
        # Use aliases if provided, otherwise build from name
        flags = list(options.aliases or [f"--{options.name}"])

        kwargs: dict[str, Any] = {
            "help": options.help_text,
        }

        if options.action:
            # Flag-style arguments
            kwargs["action"] = options.action

            if options.action == "version" and options.version:
                kwargs["version"] = options.version
        else:
            # Normal arguments that take a value
            kwargs.update(
                type=options.data_type,
                required=options.required,
                default=options.default,
                choices=options.choices,
                nargs=options.nargs,
                metavar=options.metavar,
            )

        parser.add_argument(*flags, **kwargs)
        return parser


class LocAction(argparse.Action):
    """
    Custom argparse action that prints codebase LOC/byte stats and exits,
    mirroring the behaviour of the built-in ``version`` action.
    """

    def __init__(
        self, option_strings, dest, default=argparse.SUPPRESS, **kwargs
    ):
        super().__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            **kwargs,
        )

    def __call__(self, parser, namespace, values, option_string=None):
        from mini_arcade.utils.codebase_length import (  # pylint: disable=import-outside-toplevel
            codebase_length,
        )

        s = codebase_length(
            [
                "mini_arcade",
                "mini_arcade_core",
                "mini_arcade_pygame_backend",
                "mini_arcade_native_backend",
            ]
        )
        print(
            f"Python : {s.python_loc:>7,} lines  {s.python_bytes:>10,} bytes"
        )
        print(f"C++    : {s.cpp_loc:>7,} lines  {s.cpp_bytes:>10,} bytes")
        print(f"Total  : {s.total_loc:>7,} lines  {s.total_bytes:>10,} bytes")
        parser.exit()


class GlobalParserBuilder:
    """
    Builder class to create the global parser for the CLI application.
    """

    @staticmethod
    def build_global_parser(
        version: str,
        extra_args: Optional[list[ArgumentOptions]] = None,
    ) -> argparse.ArgumentParser:
        """
        Build the global parser for the CLI application.

        :return: The global parser for the CLI application.
        :rtype: argparse.ArgumentParser
        """
        parser = argparse.ArgumentParser(
            add_help=False  # Let the real parser handle help
        )

        # Version flag
        version_opts = ArgumentOptions(
            name="version",
            aliases=["-V", "--version"],
            help_text="Show the version and exit",
            action="version",
            version=version,
        )
        ArgumentParserFactory.add_argument_parser(parser, version_opts)

        # Verbose flag
        verbose_opts = ArgumentOptions(
            name="verbose",
            aliases=["-v", "--verbose"],
            help_text="Increase verbosity (-v, -vv, -vvv)",
            action="count",
            default=0,
        )
        ArgumentParserFactory.add_argument_parser(parser, verbose_opts)

        # Codebase length flag
        loc_opts = ArgumentOptions(
            name="loc",
            aliases=["--loc"],
            help_text="Print codebase line/byte counts (Python + C++) and exit.",
            action=LocAction,
        )
        ArgumentParserFactory.add_argument_parser(parser, loc_opts)

        # Custom globals
        for opts in extra_args or []:
            ArgumentParserFactory.add_argument_parser(parser, opts)

        return parser


def apply_global_flags(args: argparse.Namespace) -> None:
    """
    Apply global flags to the runtime environment before command dispatch.

    Verbose level → root log level mapping:

    * 0 (default): ERROR  — quiet, only fatal issues visible.
    * 1 ``-v``   : WARNING
    * 2 ``-vv``  : INFO
    * 3+ ``-vvv``: DEBUG

    :param args: Namespace returned by the global parser.
    :type args: argparse.Namespace
    """
    verbose = getattr(args, "verbose", 0) or 0
    _levels = {
        0: logging.ERROR,
        1: logging.WARNING,
        2: logging.INFO,
        3: logging.DEBUG,
    }
    level = _levels.get(verbose, logging.DEBUG)
    logging.getLogger().setLevel(level)


class BaseCLIApp:
    """
    Command line interface for the IC Inspector tool.

    - Create the main parser for the CLI application.
    - Add subparsers to the main parser to handle multiple commands.
    - Add custom commands to the parser.
    """

    _commands: dict = {}

    def __init__(self, config: CLIConfig):
        """
        :param gui_callback: The callback function to run the GUI application.
        :type gui_callback: Optional[callable]
        """
        self.config = config

        self.parser = self._create_main_parser()
        self.args: Optional[argparse.Namespace] = None
        self.subparsers: Optional[argparse._SubParsersAction] = None

    def build_commands(self):
        """
        Create subparsers and register all custom commands.
        Should be called after registries are populated.
        """
        if self.subparsers is None:
            self.subparsers = self._add_subparsers(self.parser)
        self.add_custom_commands(self.subparsers)

    def _create_main_parser(self) -> argparse.ArgumentParser:
        """
        Create the main parser for the CLI application.

        :return: The main parser for the CLI application.
        :rtype: argparse.ArgumentParser
        """
        return ParserFactory.create_main_parser(self.config)

    def _add_subparsers(
        self, parser: argparse.ArgumentParser
    ) -> argparse._SubParsersAction:
        """
        Add subparsers to the main parser to handle multiple commands.

        :param parser: The main parser for the CLI application.
        :type parser: argparse.ArgumentParser

        :return: The subparsers for the main parser.
        :rtype: argparse._SubParsersAction
        """
        return parser.add_subparsers(dest="command", help="Available commands")

    def _register_command(self, command_cls: Type[BaseCommand]):
        """
        Register a command class to the CLI application.

        :param command_cls: The command class to register.
        :type command_cls: Type[BaseCommand]
        """
        self._commands[command_cls.name] = command_cls

    def add_custom_commands(self, subparsers: argparse._SubParsersAction):
        """
        Add custom commands to the parser.

        :param subparsers: The subparsers for the main parser.
        :type subparsers: argparse._SubParsersAction
        """
        for command_name in CommandRegistry.names():
            command_cls = CommandRegistry.get(command_name)
            if command_cls.name in self._commands:
                continue

            # ---- description/summary handling ----
            doc = (command_cls.__doc__ or "").strip()

            summary = command_cls.summary or (
                doc.splitlines()[0] if doc else None
            )

            command_parser = subparsers.add_parser(
                command_cls.name,
                help=summary,
                description=doc or summary,
                epilog=command_cls.epilog,
                aliases=getattr(command_cls, "aliases", ()),
                formatter_class=argparse.RawDescriptionHelpFormatter,
            )
            self.define_command_arguments(command_parser, command_cls)
            self._register_command(command_cls)

    def _get_kwargs_for_command(self, arg: ArgumentType):
        default = arg.default
        if arg.env and default is None:
            default = os.getenv(arg.env)

        kwargs = {
            "help": arg.help_text,
            "required": arg.required,
            "default": default,
        }
        if arg.choices:
            kwargs["choices"] = arg.choices
        if arg.nargs is not None:
            kwargs["nargs"] = arg.nargs
        if arg.metavar:
            kwargs["metavar"] = arg.metavar

        ty = coerce_type(arg.data_type)
        if ty is bool:
            kwargs["action"] = "store_true"
        else:
            kwargs["type"] = ty

        return kwargs

    def define_command_arguments(
        self, command_parser: argparse.ArgumentParser, command_cls: BaseCommand
    ) -> None:
        """
        Define arguments for a command.

        :param command_parser: The parser for the command.
        :type command_parser: argparse.ArgumentParser

        :param command_cls: The class for the command.
        :type command_cls: BaseCommand
        """
        for arg in command_cls.define_arguments():
            if arg.data_type is bool and arg.required:
                raise ValueError(
                    f"Boolean flag --{arg.name} cannot be required"
                )

            kwargs = self._get_kwargs_for_command(arg)

            flags = [f"--{arg.name}"]
            dashed = arg.name.replace("_", "-")
            if dashed != arg.name:
                flags.append(f"--{dashed}")

            command_parser.add_argument(*flags, **kwargs)

    def parse_args(
        self, argv: Optional[List[str]] = None
    ) -> argparse.Namespace:
        """
        Parse the command line arguments and return the parser and the parsed arguments.

        :return: The parser and the parsed arguments.
        :rtype: Tuple[argparse.ArgumentParser, argparse.Namespace]
        """
        return self.parser.parse_args(argv)

    def run(self, argv: Optional[List[str]] = None) -> int:
        """
        Run the CLI application.

        :param argv: The command line arguments to parse. If None, uses sys.argv.
        :type argv: Optional[List[str]]

        :return: The exit code of the application.
        :rtype: int
        """
        args = self.parse_args(argv)
        return self.run_command(args) or 0

    def run_command(self, args: argparse.Namespace):
        """
        Run the command based on the parsed arguments.

        :param args: The parsed arguments.
        :type args: argparse.Namespace

        :param run_callback: The callback function to run the command.
        :type run_callback: callable
        """
        if not getattr(args, "command", None):
            self.parser.print_help()
            return 1

        command_cls = CommandRegistry.get(args.command)
        if not command_cls:
            self.parser.print_help()
            return 1

        command_instance: BaseCommand = command_cls()
        cmd_args = vars(args).copy()
        cmd_args.pop("command", None)
        try:
            command_instance.validate(**cmd_args)
            return command_instance.execute(**cmd_args) or 0
        except CommandException as e:
            # logger.error(f"Error: {e}", file=sys.stderr)
            return e.exit_code
