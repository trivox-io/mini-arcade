"""
Registry for command classes with alias support.
"""

from __future__ import annotations

from typing import Callable, ClassVar, Mapping, MutableMapping, Optional, Type

from mini_arcade.cli.command_protocol import CommandProtocol
from mini_arcade.utils.implementation_registry import ImplementationRegistry


class CommandRegistry(ImplementationRegistry[CommandProtocol]):
    """
    Registry for command classes (stores classes, not instances).
    Adds alias resolution on top of ImplementationRegistry.

    :ivar implementation_base: ClassVar[type]: The base class for registered commands.
    :ivar _alias_map: ClassVar[MutableMapping[str, str]]: Mapping of aliases to
        primary command names.
    """

    # set by BaseCommand after class is defined to avoid import cycles
    implementation_base: ClassVar[
        type
    ]  # = BaseCommand  (assigned in base_command.py)

    _alias_map: ClassVar[MutableMapping[str, str]]  # alias -> primary name

    def __init_subclass__(cls, **kwargs):  # type: ignore[override]
        super().__init_subclass__(**kwargs)
        cls._alias_map = {}

    @classmethod
    def register(
        cls,
        name: str,
        impl_class: Type[CommandProtocol],
        *,
        replace: bool = False,
        aliases: tuple[str, ...] = (),
        abstract: bool = False,
    ):  # pylint: disable=too-many-arguments
        """
        Register a command class under a primary `name` and optional `aliases`.
        Abstract commands are skipped.

        :param name: The primary name of the command.
        :type name: str

        :param impl_class: The command class to register.
        :type impl_class: Type[CommandProtocol]

        :param replace: Whether to replace an existing registration.
        :type replace: bool

        :param aliases: Optional tuple of alias names for the command.
        :type aliases: tuple[str, ...]

        :param abstract: Whether the command is abstract (not registered).
        :type abstract: bool
        """
        if abstract:
            return

        # Delegate core checks and primary registration
        super().register(name, impl_class, replace=replace)

        # Record aliases -> primary name
        with cls._lock:
            for a in aliases:
                # prevent alias collisions unless replacing the same class name
                if (
                    not replace
                    and a in cls._alias_map
                    and cls._alias_map[a] != name
                ):
                    raise KeyError(
                        f"Alias '{a}' already mapped to '{cls._alias_map[a]}'"
                    )
                cls._alias_map[a] = name

    @classmethod
    def implementation(
        cls,
        name: Optional[str] = None,
        *,
        replace: bool = False,
    ) -> Callable[[Type[CommandProtocol]], Type[CommandProtocol]]:
        """
        Decorator for registering commands. Pulls metadata from class attributes:
        - name (str) if not provided here, inferred from class name
        - aliases (tuple[str, ...])  optional
        - abstract (bool)           if True, not registered

        :param name: Optional command name; defaults to class name lowercased.
        :type name: Optional[str]

        :param replace: Whether to replace an existing command with the same name.
        :type replace: bool
        """

        def decorator(
            impl_class: Type[CommandProtocol],
        ) -> Type[CommandProtocol]:
            resolved_name = (
                name
                or getattr(impl_class, "name", None)
                or cls._infer_name(impl_class)
            )
            aliases = tuple(getattr(impl_class, "aliases", ()))  # type: ignore[call-arg]
            abstract = bool(getattr(impl_class, "abstract", False))
            cls.register(
                resolved_name,
                impl_class,
                replace=replace,
                aliases=aliases,
                abstract=abstract,
            )
            return impl_class

        return decorator

    # Lookups that understand aliases
    @classmethod
    def _resolve_primary(cls, name_or_alias: str) -> str:
        if name_or_alias in cls._registry:
            return name_or_alias
        return cls._alias_map.get(name_or_alias, name_or_alias)

    @classmethod
    def get(cls, name: str) -> Type[CommandProtocol]:
        """
        Get a command class by primary name or alias.

        :param name: The primary name or alias of the command.
        :type name: str

        :return: The command class.
        :rtype: Type[CommandProtocol]
        """
        primary = cls._resolve_primary(name)
        return super().get(primary)

    @classmethod
    def try_get(cls, name: str) -> Optional[Type[CommandProtocol]]:
        """
        Try to get a command class by primary name or alias.

        :param name: The primary name or alias of the command.
        :type name: str

        :return: The command class, or None if not found.
        :rtype: Optional[Type[CommandProtocol]]
        """
        primary = cls._resolve_primary(name)
        return super().try_get(primary)

    @classmethod
    def contains(cls, name: str) -> bool:
        """
        Check if a command is registered by primary name or alias.

        :param name: The primary name or alias of the command.
        :type name: str

        :return: Whether the command is registered.
        :rtype: bool
        """
        primary = cls._resolve_primary(name)
        return super().contains(primary)

    @classmethod
    def names(cls) -> list[str]:
        """
        Primary command names only (aliases excluded).

        :return: List of primary command names.
        :rtype: list[str]
        """
        return super().names()

    @classmethod
    def all_with_aliases(cls) -> Mapping[str, Type[CommandProtocol]]:
        """
        Convenience: primary names plus alias keys.

        :return: Mapping of all names (primary + aliases) to command classes.
        :rtype: Mapping[str, Type[CommandProtocol]]
        """
        # snapshot with aliases pointing to same class
        out: dict[str, Type[CommandProtocol]] = dict(cls._registry)
        for alias, primary in cls._alias_map.items():
            if primary in cls._registry:
                out[alias] = cls._registry[primary]
        return out

    @classmethod
    def unregister(cls, name: str):
        """
        Unregister a command by primary name or alias (removes its aliases too).

        :param name: The primary name or alias of the command to unregister.
        :type name: str
        """
        with cls._lock:
            primary = cls._resolve_primary(name)
            # remove class
            cls._registry.pop(primary, None)
            # remove aliases mapped to this primary
            to_del = [a for a, p in cls._alias_map.items() if p == primary]
            for a in to_del:
                cls._alias_map.pop(a, None)

    @classmethod
    def clear(cls):
        """
        Clear all registered commands and aliases.
        """
        with cls._lock:
            super().clear()
            cls._alias_map.clear()
